from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, OwnerProfile, Listing, InterestRequest, Chat, Message, Notification, CompatibilityScore
from backend.services.email_service import notify_tenant_request_accepted, notify_tenant_request_rejected
import logging

logger = logging.getLogger(__name__)

@jwt_required()
def get_owner_listings():
    user_id = get_jwt_identity()
    owner = OwnerProfile.query.filter_by(user_id=user_id).first()
    if not owner:
        return jsonify({"error": "Forbidden: Owner role required"}), 403
        
    listings = Listing.query.filter_by(owner_id=owner.id).all()
    return jsonify([l.to_dict() for l in listings]), 200


@jwt_required()
def get_owner_requests():
    user_id = get_jwt_identity()
    owner = OwnerProfile.query.filter_by(user_id=user_id).first()
    if not owner:
        return jsonify({"error": "Forbidden: Owner role required"}), 403
        
    # Get all interest requests for listings belonging to this owner
    requests = InterestRequest.query.join(Listing).filter(Listing.owner_id == owner.id).all()
    
    results = []
    for req in requests:
        r_dict = req.to_dict()
        # Find compatibility score
        compat = CompatibilityScore.query.filter_by(tenant_id=req.tenant_id, listing_id=req.listing_id).first()
        r_dict['compatibility_score'] = compat.score if compat else None
        results.append(r_dict)
        
    return jsonify(results), 200


@jwt_required()
def accept_request(request_id):
    user_id = get_jwt_identity()
    owner = OwnerProfile.query.filter_by(user_id=user_id).first()
    if not owner:
        return jsonify({"error": "Forbidden"}), 403
        
    req = InterestRequest.query.get(request_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404
        
    if req.listing.owner_id != owner.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    if req.status != 'pending':
        return jsonify({"error": f"Request cannot be accepted because status is already '{req.status}'"}), 400
        
    try:
        req.status = 'accepted'
        
        # Enable real-time chat: check if a chat room already exists
        chat = Chat.query.filter_by(request_id=req.id).first()
        if not chat:
            chat = Chat(
                request_id=req.id,
                tenant_id=req.tenant_id,
                owner_id=owner.user_id  # Owner user ID
            )
            db.session.add(chat)
            db.session.flush()
            
            # Create introductory message
            intro_msg = Message(
                chat_id=chat.id,
                sender_id=owner.user_id,
                content="Hello! I have accepted your interest request. We can now message in real-time. Feel free to ask questions about the room!",
                is_read=False
            )
            db.session.add(intro_msg)
            
        # Create In-App Notification
        notif = Notification(
            user_id=req.tenant_id,
            message=f"Your interest request for '{req.listing.title}' has been accepted by the owner! Chat is now unlocked.",
            type="request_accepted"
        )
        db.session.add(notif)
        
        db.session.commit()
        
        # Send Email notification
        try:
            notify_tenant_request_accepted(
                tenant_email=req.tenant.email,
                owner_email=owner.user.email,
                listing_title=req.listing.title
            )
        except Exception as e:
            logger.error(f"Failed to send email to accepted tenant: {str(e)}")
            
        return jsonify({"message": "Request accepted, chat room initialized", "request": req.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to accept request", "details": str(e)}), 500


@jwt_required()
def reject_request(request_id):
    user_id = get_jwt_identity()
    owner = OwnerProfile.query.filter_by(user_id=user_id).first()
    if not owner:
        return jsonify({"error": "Forbidden"}), 403
        
    req = InterestRequest.query.get(request_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404
        
    if req.listing.owner_id != owner.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    if req.status != 'pending':
        return jsonify({"error": f"Request cannot be rejected because status is already '{req.status}'"}), 400
        
    try:
        req.status = 'rejected'
        
        # Create In-App Notification
        notif = Notification(
            user_id=req.tenant_id,
            message=f"Your interest request for '{req.listing.title}' was declined by the owner.",
            type="request_rejected"
        )
        db.session.add(notif)
        
        db.session.commit()
        
        # Send Email notification
        try:
            notify_tenant_request_rejected(
                tenant_email=req.tenant.email,
                listing_title=req.listing.title
            )
        except Exception as e:
            logger.error(f"Failed to send email to rejected tenant: {str(e)}")
            
        return jsonify({"message": "Request declined", "request": req.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to decline request", "details": str(e)}), 500
