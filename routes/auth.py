# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, skip the login screen
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.status:
            flash('Your account has been deactivated. Contact administration.', 'warning')
            return redirect(url_for('auth.login'))
            
        # Log the user in via Flask-Login session management
        login_user(user, remember=request.form.get('remember', False))
        return redirect(url_for('dashboard.index'))
        
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))