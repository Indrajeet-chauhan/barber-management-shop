# models/invoice.py
from database import db
from datetime import datetime, timezone

class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    
    # Financial metrics
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    tax = db.Column(db.Float, nullable=False, default=0.0)
    discount = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)
    
    # Metadata vectors
    payment_mode = db.Column(db.String(50), nullable=False, default='Cash') # Cash, UPI, Card, Wallet
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relational bridges
    customer = db.relationship('Customer', backref=db.backref('invoices', lazy=True))
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Invoice {self.invoice_number} - Total: ${self.total}>"


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    
    # Track the description and cost at the exact moment of sale (in case menu prices change later)
    item_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    total_price = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f"<InvoiceItem {self.item_name} x {self.quantity}>"