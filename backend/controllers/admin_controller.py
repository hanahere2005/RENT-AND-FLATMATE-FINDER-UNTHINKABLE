from flask import jsonify
from flask_jwt_extended import jwt_required
from backend.models import db, User, Listing, InterestRequest, Chat
from backend.middleware.auth_middleware import admin_required

@jwt_required()
@admin_required
def get_analytics():
    total_users = User.query.count()
    tenants_count = User.query.filter_by(role='tenant').count()
    owners_count = User.query.filter_by(role='owner').count()
    admins_count = User.query.filter_by(role='admin').count()
    
    total_listings = Listing.query.count()
    active_listings = Listing.query.filter_by(is_filled=False).count()
    filled_listings = Listing.query.filter_by(is_filled=True).count()
    
    total_requests = InterestRequest.query.count()
    pending_requests = InterestRequest.query.filter_by(status='pending').count()
    accepted_requests = InterestRequest.query.filter_by(status='accepted').count()
    rejected_requests = InterestRequest.query.filter_by(status='rejected').count()
    
    total_chats = Chat.query.count()
    
    return jsonify({
        "users": {
            "total": total_users,
            "tenants": tenants_count,
            "owners": owners_count,
            "admins": admins_count
        },
        "listings": {
            "total": total_listings,
            "active": active_listings,
            "filled": filled_listings
        },
        "requests": {
            "total": total_requests,
            "pending": pending_requests,
            "accepted": accepted_requests,
            "rejected": rejected_requests
        },
        "chats": {
            "total": total_chats
        }
    }), 200


@jwt_required()
@admin_required
def list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200


@jwt_required()
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    if user.role == 'admin':
        return jsonify({"error": "Cannot delete admin users"}), 400
        
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"User {user_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete user", "details": str(e)}), 500


@jwt_required()
@admin_required
def list_listings():
    listings = Listing.query.all()
    return jsonify([l.to_dict() for l in listings]), 200


@jwt_required()
@admin_required
def delete_listing(listing_id):
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
        
    try:
        db.session.delete(listing)
        db.session.commit()
        return jsonify({"message": f"Listing {listing_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete listing", "details": str(e)}), 500
