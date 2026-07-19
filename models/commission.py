# models/commission.py
from database import db
from datetime import datetime, timezone

class CommissionLedger(db.Model):
    __tablename__ = 'commission_ledger'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    invoice_item_id = db.Column(db.Integer, db.ForeignKey('invoice_items.id'), nullable=False)
    
    # Financial split captures
    net_sales_amount = db.Column(db.Float, nullable=False, default=0.0) # Line total after prorated discounts
    commission_rate = db.Column(db.Float, nullable=False, default=0.0) # Percentage assigned at execution time
    commission_payout = db.Column(db.Float, nullable=False, default=0.0) # Calculated cash cut value
    
    # Categorization anchor: 'Service' or 'Product'
    item_type = db.Column(db.String(50), nullable=False, default='Service')
    
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relational bindings
    employee = db.relationship('Employee', backref=db.backref('commission_lines', lazy=True))
    invoice_item = db.relationship('InvoiceItem', backref=db.backref('commission_splits', lazy=True, cascade="all, delete-orphan"))

    def calculate_payout(self):
        """Computes the final employee cut based on the net collected price."""
        self.commission_payout = round(self.net_sales_amount * (self.commission_rate / 100.0), 2)

    def __repr__(self):
        return f"<Commission Line ID: {self.id} -> Emp: {self.employee_id} Payout: ${self.commission_payout}>"