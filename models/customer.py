# models/customer.py
from database import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    address = db.Column(db.String(200), nullable=True)
    birthday = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True) # For hair formulas, preferences, or allergies
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Customer {self.name} - {self.phone}>"