# routes/service.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database import db
from models.service import Service

service_bp = Blueprint('service', __name__)

@service_bp.route('/services', methods=['GET'])
@login_required
def index():
    """List the shop service menu options."""
    services = Service.query.order_by(Service.name.asc()).all()
    return render_template('services/index.html', services=services)

@service_bp.route('/services/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new specialty service item to the operational catalog roster."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = float(request.form.get('price', 0.0))
        duration = int(request.form.get('duration', 30))
        description = request.form.get('description', '').strip() or None

        if Service.query.filter_by(name=name).first():
            flash('A service option with this matching name already exists.', 'danger')
            return redirect(url_for('service.add'))

        new_service = Service(
            name=name, price=price, duration=duration, description=description
        )
        db.session.add(new_service)
        db.session.commit()
        
        flash(f'Menu item "{name}" cataloged successfully!', 'success')
        return redirect(url_for('service.index'))

    return render_template('services/add.html')