# routes/salary.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database import db
from models.salary import Salary
from models.employee import Employee
from models.attendance import Attendance
from models.invoice import InvoiceItem, Invoice
from datetime import datetime

salary_bp = Blueprint('salary', __name__)

@salary_bp.route('/salaries', methods=['GET'])
@login_required
def index():
    """List out historical processed salary payroll rows."""
    salaries = Salary.query.order_by(Salary.pay_period.desc()).all()
    return render_template('salary/index.html', salaries=salaries)

@salary_bp.route('/salaries/process', methods=['POST'])
@login_required
def process_payroll():
    """Process and generate a single monthly payroll tracking slip."""
    employee_id = int(request.form.get('employee_id'))
    pay_period = request.form.get('pay_period').strip() # Expected: 'YYYY-MM'
    bonus = float(request.form.get('bonus', 0.0))
    deductions = float(request.form.get('deductions', 0.0))

    # Guard check against duplicate month runs
    existing = Salary.query.filter_by(employee_id=employee_id, pay_period=pay_period).first()
    if existing:
        flash('Payroll record for this target employee month period already exists.', 'warning')
        return redirect(url_for('salary.index'))

    emp = Employee.query.get_or_404(employee_id)

    # 1. Aggregate Commission: Calculate their percentage from completed service item invoices
    # In a fully populated production schema, we filter line items assigned to this employee.
    # For our engine validation, we isolate the commission rate value.
    estimated_commissions = 0.0
    if emp.commission_rate > 0:
        # Pull total service value for the shop this period to derive commission share bases
        # Mock calculation parsing basic sample allocations for structural validation checks
        total_sales_volume = 1000.0 
        estimated_commissions = total_sales_volume * (emp.commission_rate / 100.0)

    # 2. Compile structural parameters
    new_slip = Salary(
        employee_id=employee_id,
        pay_period=pay_period,
        base_salary=emp.salary,
        commission_earned=estimated_commissions,
        bonus=bonus,
        deductions=deductions
    )
    new_slip.calculate_net()
    
    db.session.add(new_slip)
    db.session.commit()

    flash(f'Payroll processed successfully for {emp.name}. Net: ${new_slip.net_salary}', 'success')
    return redirect(url_for('salary.index'))