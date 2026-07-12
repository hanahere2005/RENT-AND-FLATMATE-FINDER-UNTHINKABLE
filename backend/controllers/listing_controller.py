import json
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from backend.models import db, Listing, ListingImage, OwnerProfile, TenantProfile, CompatibilityScore
from backend.utils.helpers import save_uploaded_file
from backend.services.ai_service import calculate_compatibility
from datetime import datetime

@jwt_required()
def create_listing():
    user_id = get_jwt_identity()
    owner = OwnerProfile.query.filter_by(user_id=user_id).first()
    if not owner:
        return jsonify({"error": "Forbidden: Only registered owners can create listings"}), 403
        
    # Form data since it might contain files
    title = request.form.get('title')
    description = request.form.get('description')
    location = request.form.get('location')
    address = request.form.get('address')
    rent = request.form.get('rent')
    available_from_str = request.form.get('available_from')
    room_type = request.form.get('room_type')
    furnishing_status = request.form.get('furnishing_status')
    num_rooms = request.form.get('num_rooms', 1)
    contact_info = request.form.get('contact_info')
    
    # Parse amenities from JSON string if sent that way, or fallback to list
    amenities_raw = request.form.get('amenities')
    amenities = []
    if amenities_raw:
        try:
            amenities = json.loads(amenities_raw)
        except Exception:
            amenities = [a.strip() for a in amenities_raw.split(',') if a.strip()]
            
    if not all([title, description, location, address, rent, available_from_str, room_type, furnishing_status, contact_info]):
        return jsonify({"error": "Missing required fields"}), 400
        
    try:
        rent = float(rent)
        num_rooms = int(num_rooms)
        available_from = datetime.strptime(available_from_str, '%Y-%m-%d').date()
    except Exception as e:
        return jsonify({"error": "Invalid format for rent, num_rooms, or available_from date", "details": str(e)}), 400
        
    try:
        new_listing = Listing(
            owner_id=owner.id,
            title=title,
            description=description,
            location=location,
            address=address,
            rent=rent,
            available_from=available_from,
            room_type=room_type,
            furnishing_status=furnishing_status,
            num_rooms=num_rooms,
            amenities=amenities,
            contact_info=contact_info,
            is_filled=False
        )
        db.session.add(new_listing)
        db.session.flush()  # Generate listing id for images
        
        # Handle multiple file uploads
        uploaded_files = request.files.getlist('images')
        for file in uploaded_files:
            file_url = save_uploaded_file(file)
            if file_url:
                img = ListingImage(listing_id=new_listing.id, image_url=file_url)
                db.session.add(img)
                
        db.session.commit()
        
        # Trigger compatibility scoring background calculation for all existing tenants
        # to ensure scores are pre-computed. (Done in-line for simplicity, can be put in task queue)
        tenants = TenantProfile.query.all()
        for tenant in tenants:
            try:
                score, explanation, is_ai = calculate_compatibility(new_listing, tenant)
                compat = CompatibilityScore(
                    tenant_id=tenant.user_id,
                    listing_id=new_listing.id,
                    score=score,
                    explanation=explanation,
                    is_ai=is_ai
                )
                db.session.add(compat)
            except Exception as e:
                # Log error but don't fail the listing creation
                current_app.logger.error(f"Error pre-computing compatibility for tenant {tenant.id}: {str(e)}")
                
        db.session.commit()
        
        return jsonify({"message": "Listing created successfully", "listing": new_listing.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create listing", "details": str(e)}), 500


def get_listings():
    # Parse query filters
    location = request.args.get('location')
    budget_max = request.args.get('max_budget') or request.args.get('budget_max')
    budget_min = request.args.get('min_budget') or request.args.get('budget_min')
    room_type = request.args.get('room_type')
    furnishing = request.args.get('furnishing')
    gender = request.args.get('gender')
    lifestyle = request.args.get('lifestyle')
    search = request.args.get('search')
    move_in_date = request.args.get('move_in_date')
    sort_by = request.args.get('sort_by', 'created_at')  # 'created_at', 'rent', 'compatibility'
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    
    # Query base: only show active (not filled) listings
    query = Listing.query.filter_by(is_filled=False)
    
    # Check if a tenant is logged in to return their compatibility scores
    tenant_user_id = None
    tenant_profile = None
    try:
        verify_jwt_in_request(optional=True)
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        if claims.get('role') == 'tenant':
            tenant_user_id = int(get_jwt_identity())
            tenant_profile = TenantProfile.query.filter_by(user_id=tenant_user_id).first()
    except Exception:
        pass

    # Build prefs from query params to see if preferences were supplied
    prefs = {}
    for key, val in [
        ('location', location),
        ('max_budget', budget_max),
        ('min_budget', budget_min),
        ('room_type', room_type),
        ('furnishing', furnishing),
        ('gender', gender),
        ('lifestyle', lifestyle),
        ('search', search),
        ('move_in_date', move_in_date)
    ]:
        if val:
            prefs[key] = val

    filters_supplied = len(prefs) > 0
        
    listings_list = query.all()
    
    processed_listings = []
    for listing in listings_list:
        ldict = listing.to_dict()
        
        if tenant_profile:
            if filters_supplied:
                # Dynamic matching based on active filters
                from backend.services.ai_service import calculate_compatibility_dynamic
                score, explanation, breakdown = calculate_compatibility_dynamic(listing, prefs)
                ldict['compatibility'] = {
                    "score": score,
                    "explanation": explanation,
                    "compatibility_breakdown": breakdown,
                    "status": "Calculated dynamically"
                }
                ldict['compatibility_score'] = score
                ldict['compatibility_breakdown'] = breakdown
            else:
                # No filters supplied: compatibility is 0
                ldict['compatibility'] = {
                    "score": 0,
                    "status": "No preferences selected"
                }
                ldict['compatibility_score'] = 0
                ldict['compatibility_breakdown'] = None
        else:
            ldict['compatibility'] = None
            ldict['compatibility_score'] = None
            ldict['compatibility_breakdown'] = None
                
        processed_listings.append(ldict)
        
    # Sort listings list
    if filters_supplied and tenant_profile:
        processed_listings.sort(key=lambda x: x['compatibility']['score'] if (x.get('compatibility') and x['compatibility'].get('score') is not None) else -1, reverse=True)
    elif sort_by == 'rent':
        processed_listings.sort(key=lambda x: x['rent'])
    elif sort_by == 'compatibility' and tenant_profile:
        processed_listings.sort(key=lambda x: x['compatibility']['score'] if (x.get('compatibility') and x['compatibility'].get('score') is not None) else -1, reverse=True)
    else:  # default sorting by created_at desc
        processed_listings.sort(key=lambda x: x['created_at'], reverse=True)
        
    # Pagination
    total = len(processed_listings)
    start = (page - 1) * limit
    end = start + limit
    paginated_listings = processed_listings[start:end]
    
    return jsonify({
        "listings": paginated_listings,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }), 200


def get_listing_details(listing_id):
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
        
    # Check if search filters were supplied to the details route as query params
    location = request.args.get('location')
    budget_max = request.args.get('max_budget') or request.args.get('budget_max')
    budget_min = request.args.get('min_budget') or request.args.get('budget_min')
    room_type = request.args.get('room_type')
    furnishing = request.args.get('furnishing')
    gender = request.args.get('gender')
    lifestyle = request.args.get('lifestyle')
    search = request.args.get('search')
    move_in_date = request.args.get('move_in_date')

    prefs = {}
    for key, val in [
        ('location', location),
        ('max_budget', budget_max),
        ('min_budget', budget_min),
        ('room_type', room_type),
        ('furnishing', furnishing),
        ('gender', gender),
        ('lifestyle', lifestyle),
        ('search', search),
        ('move_in_date', move_in_date)
    ]:
        if val:
            prefs[key] = val

    filters_supplied = len(prefs) > 0

    ldict = listing.to_dict()
    ldict['compatibility'] = None
    ldict['compatibility_score'] = None
    ldict['compatibility_breakdown'] = None
    
    try:
        verify_jwt_in_request(optional=True)
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        if claims.get('role') == 'tenant':
            tenant_user_id = int(get_jwt_identity())
            tenant_profile = TenantProfile.query.filter_by(user_id=tenant_user_id).first()
            
            if filters_supplied:
                # Dynamic matching based on active filters
                from backend.services.ai_service import calculate_compatibility_dynamic
                score, explanation, breakdown = calculate_compatibility_dynamic(listing, prefs)
                ldict['compatibility'] = {
                    "score": score,
                    "explanation": explanation,
                    "compatibility_breakdown": breakdown,
                    "status": "Calculated dynamically"
                }
                ldict['compatibility_score'] = score
                ldict['compatibility_breakdown'] = breakdown
            else:
                # Fallback to tenant profile if it is configured
                is_configured = False
                if tenant_profile:
                    if tenant_profile.preferred_location and tenant_profile.preferred_location != 'Not specified':
                        is_configured = True
                    if tenant_profile.budget_max and tenant_profile.budget_max != 1000.0:
                        is_configured = True
                    if tenant_profile.lifestyle_habits:
                        is_configured = True
                        
                if is_configured:
                    compat = CompatibilityScore.query.filter_by(tenant_id=tenant_user_id, listing_id=listing.id).first()
                    if not compat:
                        # Compute on the fly
                        score, explanation, is_ai = calculate_compatibility(listing, tenant_profile)
                        compat = CompatibilityScore(
                            tenant_id=tenant_user_id,
                            listing_id=listing.id,
                            score=score,
                            explanation=explanation,
                            is_ai=is_ai
                        )
                        db.session.add(compat)
                        db.session.commit()
                    if compat:
                        compat_dict = compat.to_dict()
                        ldict['compatibility'] = compat_dict
                        ldict['compatibility_score'] = compat_dict['score']
                        ldict['compatibility_breakdown'] = compat_dict['compatibility_breakdown']
                else:
                    ldict['compatibility'] = {
                        "score": 0,
                        "status": "No preferences selected"
                    }
                    ldict['compatibility_score'] = 0
                    ldict['compatibility_breakdown'] = None
    except Exception:
        pass
        
    return jsonify(ldict), 200


@jwt_required()
def update_listing(listing_id):
    user_id = get_jwt_identity()
    owner = OwnerProfile.query.filter_by(user_id=user_id).first()
    if not owner:
        return jsonify({"error": "Forbidden"}), 403
        
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
        
    if listing.owner_id != owner.id:
        return jsonify({"error": "Unauthorized: This listing does not belong to you"}), 403
        
    # Form data
    listing.title = request.form.get('title', listing.title)
    listing.description = request.form.get('description', listing.description)
    listing.location = request.form.get('location', listing.location)
    listing.address = request.form.get('address', listing.address)
    listing.contact_info = request.form.get('contact_info', listing.contact_info)
    listing.room_type = request.form.get('room_type', listing.room_type)
    listing.furnishing_status = request.form.get('furnishing_status', listing.furnishing_status)
    
    rent = request.form.get('rent')
    if rent:
        try:
            listing.rent = float(rent)
        except ValueError:
            return jsonify({"error": "Invalid rent format"}), 400
            
    num_rooms = request.form.get('num_rooms')
    if num_rooms:
        try:
            listing.num_rooms = int(num_rooms)
        except ValueError:
            return jsonify({"error": "Invalid num_rooms format"}), 400
            
    avail = request.form.get('available_from')
    if avail:
        try:
            listing.available_from = datetime.strptime(avail, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid available_from date format"}), 400
            
    amenities_raw = request.form.get('amenities')
    if amenities_raw:
        try:
            listing.amenities = json.loads(amenities_raw)
        except Exception:
            listing.amenities = [a.strip() for a in amenities_raw.split(',') if a.strip()]
            
    # Process new image uploads
    uploaded_files = request.files.getlist('images')
    for file in uploaded_files:
        file_url = save_uploaded_file(file)
        if file_url:
            img = ListingImage(listing_id=listing.id, image_url=file_url)
            db.session.add(img)
            
    try:
        db.session.commit()
        
        # Invalidate compatibility scores and recalculate since details changed
        CompatibilityScore.query.filter_by(listing_id=listing.id).delete()
        db.session.commit()
        
        return jsonify({"message": "Listing updated successfully", "listing": listing.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update listing", "details": str(e)}), 500


@jwt_required()
def delete_listing(listing_id):
    user_id = get_jwt_identity()
    owner = OwnerProfile.query.filter_by(user_id=user_id).first()
    if not owner:
        return jsonify({"error": "Forbidden"}), 403
        
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
        
    if listing.owner_id != owner.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    try:
        db.session.delete(listing)
        db.session.commit()
        return jsonify({"message": "Listing deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete listing", "details": str(e)}), 500


@jwt_required()
def mark_listing_filled(listing_id):
    user_id = get_jwt_identity()
    owner = OwnerProfile.query.filter_by(user_id=user_id).first()
    if not owner:
        return jsonify({"error": "Forbidden"}), 403
        
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
        
    if listing.owner_id != owner.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    try:
        listing.is_filled = True
        db.session.commit()
        return jsonify({"message": "Listing marked as filled", "listing": listing.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update status", "details": str(e)}), 500
