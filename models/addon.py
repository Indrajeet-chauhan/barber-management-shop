# models/addon.py
from database import db

# Association table mapping many-to-many relationships between appointments and custom add-ons
appointment_addons = db.Table('appointment_addons',
    db.Column('appointment_id', db.Integer, db.ForeignKey('appointments.id', ondelete='CASCADE'), primary_key=True),
    db.Column('addon_id', db.Integer, db.ForeignKey('addons.id', ondelete='CASCADE'), primary_key=True)
)

class Addon(db.Model):
    __tablename__ = 'addons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True) # e.g., "Cooling Mint Shampoo", "Gold Face Mask"
    price = db.Column(db.Float, nullable=False, default=0.0)
    extra_duration = db.Column(db.Integer, nullable=False, default=10) # Additional minutes added to chair time
    status = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Addon {self.name} - +${self.price} (+{self.extra_duration} mins)>"