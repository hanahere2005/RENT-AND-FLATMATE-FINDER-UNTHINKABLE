from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, TenantProfile, User, InterestRequest, Listing, CompatibilityScore, Notification
from backend.services.ai_service import calculate_compatibility
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    profile = TenantProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({
            "success": False,
            "error": "Profile not found",
            "code": 404
        }), 404
    return jsonify({
        "success": True,
        "message": "Profile retrieved successfully",
        "data": profile.to_dict()
    }), 200


@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'tenant':
        return jsonify({
            "success": False,
            "error": "Unauthorized: Tenant role required",
            "code": 403
        }), 403
        
    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "error": "No data provided",
            "code": 400
        }), 400
        
    profile = TenantProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = TenantProfile(user_id=user_id)
        db.session.add(profile)
        
    preferred_locs = data.get('preferred_locations')
    if preferred_locs is not None:
        if isinstance(preferred_locs, list):
            profile.preferred_location = ", ".join(preferred_locs)
        else:
            profile.preferred_location = str(preferred_locs)
    elif 'preferred_location' in data:
        profile.preferred_location = data.get('preferred_location')
        
    profile.occupation = data.get('occupation', profile.occupation)
    profile.bio = data.get('bio', profile.bio)
    
    habits = data.get('lifestyle_habits')
    if habits is not None:
        if isinstance(habits, list):
            profile.lifestyle_habits = ", ".join(habits)
        else:
            profile.lifestyle_habits = str(habits)
    
    if 'budget_min' in data:
        try:
            profile.budget_min = float(data.get('budget_min'))
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid minimum budget",
                "code": 400
            }), 400
            
    if 'budget_max' in data:
        try:
            profile.budget_max = float(data.get('budget_max'))
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid maximum budget",
                "code": 400
            }), 400
            
    if 'move_in_date' in data:
        try:
            profile.move_in_date = datetime.strptime(data.get('move_in_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid move_in_date format (YYYY-MM-DD)",
                "code": 400
            }), 400
            
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
        
        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "data": profile.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to update profile",
            "details": str(e),
            "code": 500
        }), 500


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
        
    return jsonify({
        "success": True,
        "message": "Sent requests retrieved successfully",
        "data": results
    }), 200


@jwt_required()
def send_interest_request(listing_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'tenant':
        return jsonify({
            "success": False,
            "error": "Forbidden: Only tenants can send interest requests",
            "code": 403
        }), 403
        
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({
            "success": False,
            "error": "Listing not found",
            "code": 404
        }), 404
        
    # Check if request already exists
    existing = InterestRequest.query.filter_by(tenant_id=user_id, listing_id=listing_id).first()
    if existing:
        return jsonify({
            "success": False,
            "error": "You have already sent an interest request for this listing.",
            "code": 400
        }), 400
        
    try:
        req = InterestRequest(tenant_id=user_id, listing_id=listing_id, status='pending')
        db.session.add(req)
        db.session.flush()
        
        # Ensure compatibility score is generated
        compat = CompatibilityScore.query.filter_by(tenant_id=user_id, listing_id=listing_id).first()
        score = 0
        profile = TenantProfile.query.filter_by(user_id=user_id).first()
        if not compat:
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
        try:
            from backend.services.email_service import notify_owner_of_interest
            owner_email = listing.owner_profile.user.email
            
            budget_min = profile.budget_min if profile else 0.0
            budget_max = profile.budget_max if profile else 1000.0
            move_in_date = profile.move_in_date.isoformat() if profile and profile.move_in_date else 'Flexible'
            
            notify_owner_of_interest(
                owner_email=owner_email,
                listing_title=listing.title,
                tenant_email=user.email,
                budget_min=budget_min,
                budget_max=budget_max,
                move_in_date=move_in_date,
                score=score
            )
        except Exception as e:
            logger.error(f"Failed to send email alerts: {str(e)}")
            
        return jsonify({
            "success": True,
            "message": "Interest request sent successfully",
            "data": req.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to send interest request",
            "details": str(e),
            "code": 500
        }), 500
        

@jwt_required()
def get_compatibility(listing_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'tenant':
        return jsonify({
            "success": False,
            "error": "Unauthorized: Tenant role required",
            "code": 403
        }), 403
        
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({
            "success": False,
            "error": "Listing not found",
            "code": 404
        }), 404
        
    profile = TenantProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({
            "success": False,
            "error": "Tenant profile not found",
            "code": 404
        }), 404
        
    try:
        # Check if compatibility score already pre-computed
        compat = CompatibilityScore.query.filter_by(tenant_id=user_id, listing_id=listing_id).first()
        if not compat:
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
            
        # Get interest request status if any
        interest_req = InterestRequest.query.filter_by(tenant_id=user_id, listing_id=listing_id).first()
        interest_status = interest_req.status if interest_req else 'none'
        
        return jsonify({
            "success": True,
            "message": "Compatibility check retrieved successfully",
            "data": {
                "compatibility": compat.to_dict(),
                "interest_status": interest_status
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to calculate compatibility",
            "details": str(e),
            "code": 500
        }), 500
