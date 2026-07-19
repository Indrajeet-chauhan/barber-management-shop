# models/membership.py
from database import db
from datetime import datetime, timezone

class MembershipTier(db.Model):
    __tablename__ = 'membership_tiers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True) # Silver, Gold, Platinum
    monthly_fee = db.Column(db.Float, nullable=False, default=0.0)
    discount_percentage = db.Column(db.Float, nullable=False, default=0.0) # e.g., 10.0 for 10% off services
    benefits = db.Column(db.Text, nullable=True)
    status = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<MembershipTier {self.name} - Disc: {self.discount_percentage}%>"


class CustomerMembership(db.Model):
    __tablename__ = 'customer_memberships'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), unique=True, nullable=False)
    tier_id = db.Column(db.Integer, db.ForeignKey('membership_tiers.id'), nullable=False)
    
    # Subscription timelines
    start_date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    next_renewal = db.Column(db.Date, nullable=False)
    
    # State Engine: 'Active', 'Suspended', 'Expired'
    status = db.Column(db.String(50), nullable=False, default='Active', index=True)

    # Relational bindings
    customer = db.relationship('Customer', backref=db.backref('membership_profile', uselist=False, lazy=True))
    tier = db.relationship('MembershipTier', backref=db.backref('subscribers', lazy=True))

    def __repr__(self):
        return f"<CustomerMembership Cust_ID: {self.customer_id} -> Tier_ID: {self.tier_id} ({self.status})>"