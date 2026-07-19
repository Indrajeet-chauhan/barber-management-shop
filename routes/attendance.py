# routes/attendance.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database import db
from models.attendance import Attendance
from models.employee import Employee
from datetime import datetime, timezone, time

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance', methods=['GET'])
@login_required
def index():
    """List out historical daily attendance log rows."""
    logs = Attendance.query.order_by(Attendance.date.desc()).all()
    return render_template('attendance/index.html', logs=logs)

@attendance_bp.route('/attendance/check-in', methods=['POST'])
@login_required
def check_in():
    """Log a barber check-in event timestamp entry."""
    employee_id = int(request.form.get('employee_id'))
    current_date = datetime.now(timezone.utc).date()
    current_time = datetime.now(timezone.utc)

    # Business rule safeguard: block duplicate check-ins on the same calendar day
    existing_log = Attendance.query.filter_by(employee_id=employee_id, date=current_date).first()
    if existing_log:
        flash('Staff employee has already clocked in for today.', 'warning')
        return redirect(url_for('attendance.index'))

    # Evaluate tardiness: Flag as late if check-in is after 09:15 AM shop standard opening hour
    shop_cutoff = time(9, 15)
    is_late = current_time.time() > shop_cutoff

    new_log = Attendance(
        employee_id=employee_id,
        date=current_date,
        check_in=current_time,
        is_late=is_late
    )
    db.session.add(new_log)
    db.session.commit()

    flash('Check-in event recorded successfully.', 'success')
    return redirect(url_for('attendance.index'))

@attendance_bp.route('/attendance/check-out/<int:id>', methods=['POST'])
@login_required
def check_out(id):
    """Log terminal shift clock-out event timestamp adjustment."""
    log = Attendance.query.get_or_404(id)
    
    if log.check_out:
        flash('This operational shift entry record has already been closed.', 'warning')
        return redirect(url_for('attendance.index'))

    log.check_out = datetime.now(timezone.utc)
    log.calculate_hours()  # Compute performance runtime hours metrics
    db.session.commit()

    flash(f'Clock-out completed. Hours worked: {log.working_hours}', 'success')
    return redirect(url_for('attendance.index'))