# models/user.py
from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Role-Based Access Control (RBAC): 'Admin', 'Manager', 'Barber', 'Receptionist'
    role = db.Column(db.String(50), nullable=False, default='Barber')
    
    # Account status: True if active, False if suspended/fired
    status = db.Column(db.Boolean, default=True, nullable=False)

    def set_password(self, password):
        """Hashes the password using secure salt techniques."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the incoming password against the stored database hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"