# routes/employee.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database import db
from models.employee import Employee
from datetime import datetime

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/employees', methods=['GET'])
@login_required
def index():
    """List all employees in the database."""
    employees = Employee.query.order_by(Employee.name.asc()).all()
    return render_template('employees/index.html', employees=employees)

@employee_bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add():
    """Register a new staff employee profile."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip() or None
        salary = float(request.form.get('salary', 0.0))
        commission_rate = float(request.form.get('commission_rate', 0.0))
        role = request.form.get('role', 'Barber')
        
        joining_date_raw = request.form.get('joining_date', '')
        joining_date = datetime.utcnow().date()
        if joining_date_raw:
            joining_date = datetime.strptime(joining_date_raw, '%Y-%m-%d').date()

        if Employee.query.filter_by(phone=phone).first():
            flash('An employee with this phone number already exists.', 'danger')
            return redirect(url_for('employee.add'))

        new_emp = Employee(
            name=name, phone=phone, email=email, salary=salary,
            commission_rate=commission_rate, role=role, joining_date=joining_date
        )
        db.session.add(new_emp)
        db.session.commit()
        
        flash(f'Staff member {name} registered successfully!', 'success')
        return redirect(url_for('employee.index'))

    return render_template('employees/add.html')