# models/payment.py
from database import db
from datetime import datetime, timezone

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    
    # Financial capture records
    amount = db.Column(db.Float, nullable=False, default=0.0)
    gateway = db.Column(db.String(50), nullable=False, default='Cash') # Cash, Stripe, Razorpay
    
    # Unique reference hash code returned from digital payment vendor webhooks
    transaction_ref = db.Column(db.String(100), unique=True, nullable=True, index=True)
    
    # Lifecycle Status Engine: 'Pending', 'Success', 'Failed', 'Refunded'
    status = db.Column(db.String(50), nullable=False, default='Pending', index=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relational link connecting transaction item directly to the core invoice document header
    invoice = db.relationship('Invoice', backref=db.backref('payment_records', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Payment ID: {self.id} - Ref: {self.transaction_ref} - Status: {self.status}>"