from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, TenantProfile, User, InterestRequest, Listing, CompatibilityScore, Notification
from backend.services.ai_service import calculate_compatibility
from datetime import datetime

@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    profile = TenantProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify(profile.to_dict()), 200

@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'tenant':
        return jsonify({"error": "Unauthorized: Tenant role required"}), 403
        
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    profile = TenantProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = TenantProfile(user_id=user_id)
        db.session.add(profile)
        
    profile.preferred_location = data.get('preferred_location', profile.preferred_location)
    profile.occupation = data.get('occupation', profile.occupation)
    profile.bio = data.get('bio', profile.bio)
    
    if 'budget_min' in data:
        try:
            profile.budget_min = float(data.get('budget_min'))
        except ValueError:
            return jsonify({"error": "Invalid minimum budget"}), 400
            
    if 'budget_max' in data:
        try:
            profile.budget_max = float(data.get('budget_max'))
        except ValueError:
            return jsonify({"error": "Invalid maximum budget"}), 400
            
    if 'move_in_date' in data:
        try:
            profile.move_in_date = datetime.strptime(data.get('move_in_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid move_in_date format (YYYY-MM-DD)"}), 400
            
    try:
        db.session.commit()
        
        # Invalidate compatibility scores and recalculate for all active listings
        CompatibilityScore.query.filter_by(tenant_id=user_id).delete()
        db.session.commit()
        
        active_listings = Listing.query.filter_by(is_filled=False).all()
        for listing in active_listings:
            try:
                score, explanation, is_ai = calculate_compatibility(listing, profile)
                compat = CompatibilityScore(
                    tenant_id=user_id,
                    listing_id=listing.id,
                    score=score,
                    explanation=explanation,
                    is_ai=is_ai
                )
                db.session.add(compat)
            except Exception:
                pass # skip listing if matching fails
                
        db.session.commit()
        
        return jsonify({"message": "Profile updated successfully", "profile": profile.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update profile", "details": str(e)}), 500


@jwt_required()
def get_sent_requests():
    user_id = get_jwt_identity()
    requests = InterestRequest.query.filter_by(tenant_id=user_id).all()
    
    results = []
    for req in requests:
        r_dict = req.to_dict()
        # Attach compatibility score
        compat = CompatibilityScore.query.filter_by(tenant_id=user_id, listing_id=req.listing_id).first()
        r_dict['compatibility_score'] = compat.score if compat else None
        results.append(r_dict)
        
    return jsonify(results), 200

@jwt_required()
def send_interest_request(listing_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'tenant':
        return jsonify({"error": "Forbidden: Only tenants can send interest requests"}), 403
        
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
        
    # Check if request already exists
    existing = InterestRequest.query.filter_by(tenant_id=user_id, listing_id=listing_id).first()
    if existing:
        return jsonify({"error": "You have already sent an interest request for this listing."}), 400
        
    try:
        req = InterestRequest(tenant_id=user_id, listing_id=listing_id, status='pending')
        db.session.add(req)
        db.session.flush()
        
        # Ensure compatibility score is generated
        compat = CompatibilityScore.query.filter_by(tenant_id=user_id, listing_id=listing_id).first()
        score = 0
        if not compat:
            profile = TenantProfile.query.filter_by(user_id=user_id).first()
            if profile:
                score, explanation, is_ai = calculate_compatibility(listing, profile)
                compat = CompatibilityScore(
                    tenant_id=user_id,
                    listing_id=listing_id,
                    score=score,
                    explanation=explanation,
                    is_ai=is_ai
                )
                db.session.add(compat)
                db.session.commit()
                score = compat.score
        else:
            score = compat.score
            
        # Create In-App Notification for Owner
        owner_user_id = listing.owner_profile.user_id
        notif = Notification(
            user_id=owner_user_id,
            message=f"Tenant ({user.email}) is interested in your listing '{listing.title}' with compatibility score {score}%.",
            type="interest_request"
        )
        db.session.add(notif)
        db.session.commit()
        
        # Email notifications:
        # 1. Standard email to Owner
        # 2. If score > 80, triggers high compatibility email
        try:
            from backend.services.email_service import notify_owner_of_high_compatibility_interest
            owner_email = listing.owner_profile.user.email
            
            if score and score >= 80:
                notify_owner_of_high_compatibility_interest(
                    owner_email=owner_email,
                    tenant_email=user.email,
                    listing_title=listing.title,
                    score=score
                )
            else:
                from backend.services.email_service import send_email
                send_email(
                    subject="🏠 New Interested Tenant Alert",
                    recipient=owner_email,
                    body_text=f"A tenant ({user.email}) has shown interest in your listing '{listing.title}'. Check your dashboard to view details.",
                    body_html=f"<p>A tenant (<strong>{user.email}</strong>) has shown interest in your listing <strong>'{listing.title}'</strong>. Check your dashboard to view details.</p>"
                )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to send email alerts: {str(e)}")
            
        return jsonify({"message": "Interest request sent successfully", "request": req.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to send interest request", "details": str(e)}), 500
        
@jwt_required()
def get_compatibility(listing_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'tenant':
        return jsonify({"error": "Unauthorized: Tenant role required"}), 403
        
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
        
    profile = TenantProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"error": "Tenant profile not found"}), 404
        
    # Check or compute compatibility score
    compat = CompatibilityScore.query.filter_by(tenant_id=user_id, listing_id=listing_id).first()
    if not compat:
        try:
            score, explanation, is_ai = calculate_compatibility(listing, profile)
            compat = CompatibilityScore(
                tenant_id=user_id,
                listing_id=listing_id,
                score=score,
                explanation=explanation,
                is_ai=is_ai
            )
            db.session.add(compat)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to calculate compatibility", "details": str(e)}), 500
            
    # Check interest request status
    req = InterestRequest.query.filter_by(tenant_id=user_id, listing_id=listing_id).first()
    interest_status = req.status if req else 'none'
    
    return jsonify({
        "compatibility": compat.to_dict(),
        "interest_status": interest_status
    }), 200
