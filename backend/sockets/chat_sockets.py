from flask import request
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from backend.models import db, Message, Chat, User
import logging

logger = logging.getLogger(__name__)

# Dictionary to map user_id -> set of connection sids (active connections)
online_users = {}

def register_socket_events(socketio):
    
    @socketio.on('connect')
    def handle_connect(auth=None):
        token = None
        if auth and 'token' in auth:
            token = auth['token']
        if not token:
            token = request.args.get('token')
            
        if not token:
            logger.warning("Socket connection rejected: No token provided.")
            return False  # Reject connection
            
        if token.startswith('Bearer '):
            token = token.split(' ')[1]
            
        try:
            decoded = decode_token(token)
            user_id = int(decoded['sub'])
            
            # Map session ID to user ID
            request_sid = request.sid
            if user_id not in online_users:
                online_users[user_id] = set()
            online_users[user_id].add(request_sid)
            
            logger.info(f"User {user_id} connected via SocketIO. SID: {request_sid}")
            
            # Broadcast user's online status
            emit('user_status_change', {'user_id': user_id, 'status': 'online'}, broadcast=True)
            
            # Send list of online user IDs back to connecting client
            emit('online_users_list', list(online_users.keys()))
            
        except Exception as e:
            logger.error(f"Socket connection rejected: Invalid token. Error: {str(e)}")
            return False  # Reject connection

    @socketio.on('disconnect')
    def handle_disconnect():
        request_sid = request.sid
        user_id_to_remove = None
        
        # Find which user this sid belonged to
        for user_id, sids in list(online_users.items()):
            if request_sid in sids:
                sids.remove(request_sid)
                if not sids:
                    user_id_to_remove = user_id
                    del online_users[user_id]
                break
                
        if user_id_to_remove:
            logger.info(f"User {user_id_to_remove} completely disconnected.")
            # Broadcast offline status
            emit('user_status_change', {'user_id': user_id_to_remove, 'status': 'offline'}, broadcast=True)

    @socketio.on('join_chat')
    def handle_join_chat(data):
        try:
            chat_id = data.get('chat_id')
            if not chat_id:
                return
            
            chat_id = int(chat_id)
            room = f"chat_{chat_id}"
            join_room(room)
            logger.info(f"Socket SID {request.sid} joined room {room}")
        except Exception as e:
            logger.error(f"Error in join_chat: {str(e)}")

    @socketio.on('leave_chat')
    def handle_leave_chat(data):
        try:
            chat_id = data.get('chat_id')
            if not chat_id:
                return
            
            chat_id = int(chat_id)
            room = f"chat_{chat_id}"
            leave_room(room)
            logger.info(f"Socket SID {request.sid} left room {room}")
        except Exception as e:
            logger.error(f"Error in leave_chat: {str(e)}")

    @socketio.on('send_message')
    def handle_send_message(data):
        try:
            chat_id = data.get('chat_id')
            sender_id = data.get('sender_id')
            content = data.get('content')
            
            if not chat_id or not sender_id or not content:
                logger.warning("Invalid send_message details.")
                return
                
            chat_id = int(chat_id)
            sender_id = int(sender_id)
            
            # Verify chat exists and sender is participant
            chat = Chat.query.get(chat_id)
            if not chat or (chat.tenant_id != sender_id and chat.owner_id != sender_id):
                logger.warning(f"Unauthorized chat message attempt by user {sender_id} in chat {chat_id}")
                return
                
            # Save message to DB
            message = Message(
                chat_id=chat_id,
                sender_id=sender_id,
                content=content,
                is_read=False
            )
            db.session.add(message)
            db.session.commit()
            
            # Emit message to the room
            room = f"chat_{chat_id}"
            serialized = message.to_dict()
            emit('receive_message', serialized, room=room)
            
            # Identify recipient ID
            recipient_id = chat.owner_id if sender_id == chat.tenant_id else chat.tenant_id
            
            # Send global notification event to recipient if they are online
            if recipient_id in online_users:
                # We emit to each sid they have connected
                for sid in online_users[recipient_id]:
                    emit('new_message_notification', {
                        'chat_id': chat_id,
                        'message': serialized
                    }, room=sid)
                    
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in send_message: {str(e)}")

    @socketio.on('typing')
    def handle_typing(data):
        try:
            chat_id = data.get('chat_id')
            user_id = data.get('user_id')
            if chat_id and user_id:
                chat_id = int(chat_id)
                user_id = int(user_id)
                room = f"chat_{chat_id}"
                emit('user_typing', {'chat_id': chat_id, 'user_id': user_id, 'is_typing': True}, room=room, include_self=False)
        except Exception:
            pass

    @socketio.on('stop_typing')
    def handle_stop_typing(data):
        try:
            chat_id = data.get('chat_id')
            user_id = data.get('user_id')
            if chat_id and user_id:
                chat_id = int(chat_id)
                user_id = int(user_id)
                room = f"chat_{chat_id}"
                emit('user_typing', {'chat_id': chat_id, 'user_id': user_id, 'is_typing': False}, room=room, include_self=False)
        except Exception:
            pass

    @socketio.on('mark_read')
    def handle_mark_read(data):
        try:
            chat_id = data.get('chat_id')
            user_id = data.get('user_id')  # user who read the messages
            if not chat_id or not user_id:
                return
                
            chat_id = int(chat_id)
            user_id = int(user_id)
            
            # Update all unread messages sent by OTHER user in this chat
            unread_messages = Message.query.filter_by(chat_id=chat_id, is_read=False).filter(Message.sender_id != user_id).all()
            if unread_messages:
                for msg in unread_messages:
                    msg.is_read = True
                db.session.commit()
                
                # Signal the room that messages were read
                room = f"chat_{chat_id}"
                emit('messages_marked_read', {'chat_id': chat_id, 'reader_id': user_id}, room=room)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in mark_read socket event: {str(e)}")
