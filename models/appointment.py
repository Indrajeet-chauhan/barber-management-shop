# models/appointment.py
from database import db
from models.addon import appointment_addons  # <-- Import the association table

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    service_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Confirmed')

    # Relational bindings
    customer = db.relationship('Customer', backref=db.backref('appointments', lazy=True))
    employee = db.relationship('Employee', backref=db.backref('appointments', lazy=True))
    
    # New Field Addition for Module 18: Many-to-many relationship mapping tool
    addons = db.relationship('Addon', secondary=appointment_addons, backref=db.backref('linked_appointments', lazy=True))

    def get_total_duration(self, base_duration=30):
        """Calculates total operational runtime by adding up custom add-on minutes."""
        extra_minutes = sum(addon.extra_duration for addon in self.addons)
        return base_duration + extra_minutes

    def __repr__(self):
        return f"<Appointment ID: {self.id} - Service: {self.service_name}>"