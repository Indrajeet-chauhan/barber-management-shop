# models/employee.py
from database import db
from datetime import datetime, timezone

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True) # <-- Added for Module 17
    
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    salary = db.Column(db.Float, nullable=False, default=0.0)
    commission_rate = db.Column(db.Float, nullable=False, default=0.0)
    joining_date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    role = db.Column(db.String(50), nullable=False, default='Barber')
    status = db.Column(db.Boolean, default=True, nullable=False)

    # Relational bridge connecting employee back to their home branch anchor
    branch = db.relationship('Branch', backref=db.backref('staff_roster', lazy=True))

    def __repr__(self):
        return f"<Employee {self.name} - Branch ID: {self.branch_id}>"