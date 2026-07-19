# models/attendance.py
from database import db
from datetime import datetime, timezone

class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Date and structural clocking time vectors
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    check_in = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    check_out = db.Column(db.DateTime, nullable=True)
    
    # Computed metrics
    working_hours = db.Column(db.Float, nullable=False, default=0.0)
    is_late = db.Column(db.Boolean, nullable=False, default=False)

    # Relational bridge connecting entry row to staff profile
    employee = db.relationship('Employee', backref=db.backref('attendance_logs', lazy=True))

    # Add a compound index to avoid duplicate clock-ins on the same calendar day
    __table_args__ = (
        db.Index('idx_emp_date', 'employee_id', 'date'),
    )

    def calculate_hours(self):
        """Computes structural decimal elapsed time between check points."""
        if self.check_in and self.check_out:
            delta = self.check_out - self.check_in
            self.working_hours = round(delta.total_seconds() / 3600.0, 2)

    def __repr__(self):
        return f"<Attendance ID: {self.employee_id} - Date: {self.date} - Hours: {self.working_hours}>"