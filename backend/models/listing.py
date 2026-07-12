from datetime import datetime
from . import db

class Listing(db.Model):
    __tablename__ = 'listings'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False, index=True)
    address = db.Column(db.Text, nullable=False)
    rent = db.Column(db.Float, nullable=False)
    available_from = db.Column(db.Date, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # 'single', 'shared', 'entire_flat'
    furnishing_status = db.Column(db.String(50), nullable=False)  # 'unfurnished', 'semi-furnished', 'fully-furnished'
    num_rooms = db.Column(db.Integer, nullable=False, default=1)
    amenities = db.Column(db.JSON, nullable=False, default=list)  # list of strings e.g. ["wifi", "ac"]
    contact_info = db.Column(db.String(100), nullable=False)
    is_filled = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner_profile = db.relationship('OwnerProfile', back_populates='listings')
    images = db.relationship('ListingImage', back_populates='listing', cascade="all, delete-orphan")
    compatibility_scores = db.relationship('CompatibilityScore', back_populates='listing', cascade="all, delete-orphan")
    interest_requests = db.relationship('InterestRequest', back_populates='listing', cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'owner_user_id': self.owner_profile.user_id if self.owner_profile else None,
            'owner_email': self.owner_profile.user.email if self.owner_profile and self.owner_profile.user else None,
            'owner_phone': self.owner_profile.contact_phone if self.owner_profile else None,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'address': self.address,
            'rent': self.rent,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'room_type': self.room_type,
            'furnishing_status': self.furnishing_status,
            'num_rooms': self.num_rooms,
            'amenities': self.amenities,
            'contact_info': self.contact_info,
            'is_filled': self.is_filled,
            'images': [img.to_dict() for img in self.images],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ListingImage(db.Model):
    __tablename__ = 'listing_images'
    
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    listing = db.relationship('Listing', back_populates='images')
    
    def to_dict(self):
        return {
            'id': self.id,
            'listing_id': self.listing_id,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
