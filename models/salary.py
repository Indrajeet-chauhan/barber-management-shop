# models/salary.py
from database import db
from datetime import datetime, timezone

class Salary(db.Model):
    __tablename__ = 'salaries'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Target pay period window string (Format: YYYY-MM, e.g., '2026-07')
    pay_period = db.Column(db.String(7), nullable=False, index=True)
    
    # Financial breakdowns
    base_salary = db.Column(db.Float, nullable=False, default=0.0)
    commission_earned = db.Column(db.Float, nullable=False, default=0.0)
    bonus = db.Column(db.Float, nullable=False, default=0.0)
    deductions = db.Column(db.Float, nullable=False, default=0.0)
    net_salary = db.Column(db.Float, nullable=False, default=0.0)
    
    payment_status = db.Column(db.String(50), nullable=False, default='Pending') # Pending, Paid
    processed_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    employee = db.relationship('Employee', backref=db.backref('salary_slips', lazy=True))

    # Protect against duplicate month runs for the same employee
    __table_args__ = (
        db.Index('idx_emp_period', 'employee_id', 'pay_period', unique=True),
    )

    def calculate_net(self):
        """Calculates final net totals using fundamental billing fields."""
        self.net_salary = round((self.base_salary + self.commission_earned + self.bonus) - self.deductions, 2)
        if self.net_salary < 0:
            self.net_salary = 0.0

    def __repr__(self):
        return f"<Salary ID: {self.employee_id} - Period: {self.pay_period} - Net: ${self.net_salary}>"