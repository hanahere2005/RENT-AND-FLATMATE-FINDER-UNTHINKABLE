from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, Notification

@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notifications]), 200


@jwt_required()
def mark_read(notification_id):
    user_id = get_jwt_identity()
    notif = Notification.query.get(notification_id)
    if not notif:
        return jsonify({"error": "Notification not found"}), 404
        
    if str(notif.user_id) != str(user_id):
        return jsonify({"error": "Unauthorized"}), 403
        
    try:
        notif.is_read = True
        db.session.commit()
        return jsonify({"message": "Notification marked as read", "notification": notif.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update notification", "details": str(e)}), 500


@jwt_required()
def mark_all_read():
    user_id = get_jwt_identity()
    try:
        unread = Notification.query.filter_by(user_id=user_id, is_read=False).all()
        for notif in unread:
            notif.is_read = True
        db.session.commit()
        return jsonify({"message": "All notifications marked as read"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update notifications", "details": str(e)}), 500
