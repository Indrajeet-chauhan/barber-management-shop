# models/loyalty.py
from database import db
from datetime import datetime, timezone

class LoyaltyAccount(db.Model):
    __tablename__ = 'loyalty_accounts'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), unique=True, nullable=False)
    points_balance = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationship map
    customer = db.relationship('Customer', backref=db.backref('loyalty_account', uselist=False, lazy=True))

    def __repr__(self):
        return f"<LoyaltyAccount Cust_ID: {self.customer_id} - Balance: {self.points_balance}>"


class LoyaltyTransaction(db.Model):
    __tablename__ = 'loyalty_transactions'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Type tracking: 'Earned' or 'Redeemed'
    transaction_type = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<LoyaltyTransaction Cust_ID: {self.customer_id} -> {self.transaction_type} {self.points} pts>"