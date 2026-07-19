# routes/appointment.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database import db
from models.appointment import Appointment
from datetime import datetime

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/appointments', methods=['GET'])
@login_required
def index():
    """List all scheduled appointments."""
    appointments = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return render_template('appointments/index.html', appointments=appointments)

@appointment_bp.route('/appointments/book', methods=['GET', 'POST'])
@login_required
def book():
    """Book a new appointment or catch scheduling conflicts."""
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id'))
        employee_id = int(request.form.get('employee_id'))
        date_str = request.form.get('date')  # Expected: YYYY-MM-DD
        time_str = request.form.get('time')  # Expected: HH:MM
        service_name = request.form.get('service_name', '').strip()

        # Parse date and time elements cleanly
        appt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        appt_time = datetime.strptime(time_str, '%H:%M').time()

        # CONFLICT DETECTOR: Look for overlapping slots for the same barber at the exact same day/time
        conflict = Appointment.query.filter_by(
            employee_id=employee_id,
            date=appt_date,
            time=appt_time
        ).first()

        if conflict:
            flash('Scheduling Conflict: The selected barber is already booked at this time slot.', 'danger')
            return redirect(url_for('appointment.index'))

        new_appointment = Appointment(
            customer_id=customer_id,
            employee_id=employee_id,
            date=appt_date,
            time=appt_time,
            service_name=service_name,
            status='Confirmed'
        )
        db.session.add(new_appointment)
        db.session.commit()

        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointment.index'))

    return render_template('appointments/book.html')