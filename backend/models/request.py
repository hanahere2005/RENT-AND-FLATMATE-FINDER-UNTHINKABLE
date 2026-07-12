from datetime import datetime
from . import db

class InterestRequest(db.Model):
    __tablename__ = 'interest_requests'
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'listing_id', name='_tenant_listing_req_uc'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'accepted', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('User', foreign_keys=[tenant_id])
    listing = db.relationship('Listing', back_populates='interest_requests')
    chat = db.relationship('Chat', back_populates='request', uselist=False, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'tenant_email': self.tenant.email if self.tenant else None,
            'tenant_profile': self.tenant.tenant_profile.to_dict() if self.tenant and self.tenant.tenant_profile else None,
            'listing_id': self.listing_id,
            'listing_title': self.listing.title if self.listing else None,
            'listing_rent': self.listing.rent if self.listing else None,
            'listing_location': self.listing.location if self.listing else None,
            'listing_is_filled': self.listing.is_filled if self.listing else False,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
