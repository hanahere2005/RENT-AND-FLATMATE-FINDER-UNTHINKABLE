from datetime import datetime
from . import db

class TenantProfile(db.Model):
    __tablename__ = 'tenant_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    preferred_location = db.Column(db.String(100), nullable=False)
    budget_min = db.Column(db.Float, nullable=False, default=0.0)
    budget_max = db.Column(db.Float, nullable=False)
    move_in_date = db.Column(db.Date, nullable=False)
    occupation = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='tenant_profile')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.user.email if self.user else None,
            'preferred_location': self.preferred_location,
            'budget_min': self.budget_min,
            'budget_max': self.budget_max,
            'move_in_date': self.move_in_date.isoformat() if self.move_in_date else None,
            'occupation': self.occupation,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class OwnerProfile(db.Model):
    __tablename__ = 'owner_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    company_name = db.Column(db.String(100), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='owner_profile')
    listings = db.relationship('Listing', back_populates='owner_profile', cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.user.email if self.user else None,
            'company_name': self.company_name,
            'contact_phone': self.contact_phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
