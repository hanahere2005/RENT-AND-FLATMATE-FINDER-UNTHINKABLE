from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, Chat, Message

@jwt_required()
def get_chats():
    user_id = int(get_jwt_identity())
    
    # Fetch chats where user is either the tenant or the owner
    chats = Chat.query.filter((Chat.tenant_id == user_id) | (Chat.owner_id == user_id)).all()
    
    # Serialize chats and pass the user_id to count unread messages and identify the other user
    serialized_chats = [chat.to_dict(current_user_id=user_id) for chat in chats]
    
    # Sort chats by last message timestamp (most recent first) or creation date
    serialized_chats.sort(
        key=lambda x: x['last_message']['created_at'] if x['last_message'] else x['created_at'],
        reverse=True
    )
    
    return jsonify(serialized_chats), 200


@jwt_required()
def get_chat_history(chat_id):
    user_id = int(get_jwt_identity())
    
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
        
    # Verify authorization
    if chat.tenant_id != user_id and chat.owner_id != user_id:
        return jsonify({"error": "Forbidden: You are not a participant in this chat"}), 403
        
    messages = chat.messages  # Ordered by created_at ascending in DB relationship
    
    # Mark messages from the OTHER user as read since we are viewing the chat
    unread_messages = Message.query.filter_by(chat_id=chat_id, is_read=False).filter(Message.sender_id != user_id).all()
    if unread_messages:
        for msg in unread_messages:
            msg.is_read = True
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            
    return jsonify([msg.to_dict() for msg in messages]), 200
