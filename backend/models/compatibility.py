from datetime import datetime
from . import db

class CompatibilityScore(db.Model):
    __tablename__ = 'compatibility_scores'
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'listing_id', name='_tenant_listing_uc'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    is_ai = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('User', foreign_keys=[tenant_id])
    listing = db.relationship('Listing', back_populates='compatibility_scores')
    
    def to_dict(self):
        import json
        explanation_text = self.explanation
        breakdown = {
            "budget": 0,
            "location": 0,
            "lifestyle": 0,
            "gender": 0,
            "occupancy": 0,
            "amenities": 0
        }
        try:
            data = json.loads(self.explanation)
            explanation_text = data.get('text', self.explanation)
            breakdown = data.get('breakdown', breakdown)
        except Exception:
            pass
            
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'listing_id': self.listing_id,
            'score': self.score,
            'explanation': explanation_text,
            'compatibility_breakdown': breakdown,
            'is_ai': self.is_ai,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
