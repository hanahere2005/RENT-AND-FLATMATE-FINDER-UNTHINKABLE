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
        return jsonify({
            "success": False,
            "error": "Forbidden: Owner role required",
            "code": 403
        }), 403
        
    listings = Listing.query.filter_by(owner_id=owner.id).all()
    return jsonify({
        "success": True,
        "message": "Listings retrieved successfully",
        "data": [l.to_dict() for l in listings]
    }), 200


@jwt_required()
def get_owner_requests():
    user_id = get_jwt_identity()
    owner = OwnerProfile.query.filter_by(user_id=user_id).first()
    if not owner:
        return jsonify({
            "success": False,
            "error": "Forbidden: Owner role required",
            "code": 403
        }), 403
        
    # Get all interest requests for listings belonging to this owner
    requests = InterestRequest.query.join(Listing).filter(Listing.owner_id == owner.id).all()
    
    results = []
    for req in requests:
        r_dict = req.to_dict()
        # Find compatibility score
        compat = CompatibilityScore.query.filter_by(tenant_id=req.tenant_id, listing_id=req.listing_id).first()
        r_dict['compatibility'] = compat.to_dict() if compat else None
        results.append(r_dict)
        
    return jsonify({
        "success": True,
        "message": "Tenant requests retrieved successfully",
        "data": results
    }), 200


@jwt_required()
def accept_request(request_id):
    user_id = get_jwt_identity()
    owner = OwnerProfile.query.filter_by(user_id=user_id).first()
    if not owner:
        return jsonify({
            "success": False,
            "error": "Forbidden: Owner role required",
            "code": 403
        }), 403
        
    req = InterestRequest.query.get(request_id)
    if not req:
        return jsonify({
            "success": False,
            "error": "Request not found",
            "code": 404
        }), 404
        
    if req.listing.owner_id != owner.id:
        return jsonify({
            "success": False,
            "error": "Unauthorized to update this request",
            "code": 403
        }), 403
        
    if req.status != 'pending':
        return jsonify({
            "success": False,
            "error": f"Request cannot be accepted because status is already '{req.status}'",
            "code": 400
        }), 400
        
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
            owner_name = owner.company_name or owner.user.email.split('@')[0].capitalize()
            notify_tenant_request_accepted(
                tenant_email=req.tenant.email,
                owner_name=owner_name,
                owner_email=owner.user.email,
                listing_title=req.listing.title
            )
        except Exception as e:
            logger.error(f"Failed to send email to accepted tenant: {str(e)}")
            
        return jsonify({
            "success": True,
            "message": "Request accepted, chat room initialized",
            "data": req.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to accept request",
            "details": str(e),
            "code": 500
        }), 500


@jwt_required()
def reject_request(request_id):
    user_id = get_jwt_identity()
    owner = OwnerProfile.query.filter_by(user_id=user_id).first()
    if not owner:
        return jsonify({
            "success": False,
            "error": "Forbidden: Owner role required",
            "code": 403
        }), 403
        
    req = InterestRequest.query.get(request_id)
    if not req:
        return jsonify({
            "success": False,
            "error": "Request not found",
            "code": 404
        }), 404
        
    if req.listing.owner_id != owner.id:
        return jsonify({
            "success": False,
            "error": "Unauthorized to update this request",
            "code": 403
        }), 403
        
    if req.status != 'pending':
        return jsonify({
            "success": False,
            "error": f"Request cannot be rejected because status is already '{req.status}'",
            "code": 400
        }), 400
        
    try:
        req.status = 'declined'
        
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
            
        return jsonify({
            "success": True,
            "message": "Request declined",
            "data": req.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to decline request",
            "details": str(e),
            "code": 500
        }), 500


@jwt_required()
def update_request_status(request_id):
    """
    Standardized request handler mapped to PUT /owner/requests/<request_id> payload.
    Supports status updates for 'accepted' and 'rejected'/'declined'.
    """
    data = request.get_json() or {}
    status = data.get('status', '').strip().lower()
    
    if status in ['accepted', 'accept']:
        return accept_request(request_id)
    elif status in ['rejected', 'decline', 'declined', 'reject']:
        return reject_request(request_id)
    else:
        return jsonify({
            "success": False,
            "error": f"Invalid request status '{status}'. Must be 'accepted' or 'rejected'.",
            "code": 400
        }), 400
