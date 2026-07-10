from datetime import datetime
from . import db

class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('interest_requests.id', ondelete='SET NULL'), nullable=True, unique=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    request = db.relationship('InterestRequest', back_populates='chat')
    tenant = db.relationship('User', foreign_keys=[tenant_id])
    owner = db.relationship('User', foreign_keys=[owner_id])
    messages = db.relationship('Message', back_populates='chat', cascade="all, delete-orphan", order_by="Message.created_at.asc()")
    
    def to_dict(self, current_user_id=None):
        # Determine the other user in the chat
        other_user = self.owner if current_user_id == self.tenant_id else self.tenant
        
        # Determine unread message count
        unread_count = 0
        if current_user_id:
            unread_count = sum(1 for m in self.messages if not m.is_read and m.sender_id != current_user_id)
            
        last_message = self.messages[-1].to_dict() if self.messages else None
        
        return {
            'id': self.id,
            'request_id': self.request_id,
            'tenant_id': self.tenant_id,
            'owner_id': self.owner_id,
            'other_user': {
                'id': other_user.id,
                'email': other_user.email,
                'role': other_user.role,
                'profile': other_user.tenant_profile.to_dict() if other_user.role == 'tenant' and other_user.tenant_profile else (other_user.owner_profile.to_dict() if other_user.role == 'owner' and other_user.owner_profile else None)
            } if other_user else None,
            'last_message': last_message,
            'unread_count': unread_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id', ondelete='CASCADE'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    chat = db.relationship('Chat', back_populates='messages')
    sender = db.relationship('User', foreign_keys=[sender_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'sender_id': self.sender_id,
            'sender_email': self.sender.email if self.sender else None,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
