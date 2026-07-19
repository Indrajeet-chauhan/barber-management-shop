# models/service.py
from database import db

class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    duration = db.Column(db.Integer, nullable=False, default=30) # Duration in minutes
    description = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Boolean, default=True, nullable=False) # Active menu item vs. Retired service

    def __repr__(self):
        return f"<Service {self.name} - ${self.price} ({self.duration} mins)>"