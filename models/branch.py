# models/branch.py
from database import db

class Branch(db.Model):
    __tablename__ = 'branches'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True) # e.g., "Downtown Corporate", "West End Mall"
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.Boolean, default=True, nullable=False) # Active vs. Temporarily Closed

    def __repr__(self):
        return f"<Branch {self.name} - ID: {self.id}>"