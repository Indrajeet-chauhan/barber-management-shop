# routes/addon.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database import db
from models.addon import Addon

addon_bp = Blueprint('addon', __name__)

@addon_bp.route('/addons', methods=['GET'])
@login_required
def index():
    """List all diagnostic premium treatment upgrade add-ons available."""
    addons = Addon.query.order_by(Addon.name.asc()).all()
    return render_template('addons/index.html', addons=addons)

@addon_bp.route('/addons/add', methods=['POST'])
@login_required
def add_addon():
    """Catalog a brand new customizable treatment option upgrade configuration."""
    name = request.form.get('name', '').strip()
    price = float(request.form.get('price', 0.0))
    extra_duration = int(request.form.get('extra_duration', 10))

    if Addon.query.filter_by(name=name).first():
        flash('A customization add-on treatment package variant with this matching name already exists.', 'danger')
        return redirect(url_for('addon.index'))

    new_addon = Addon(name=name, price=price, extra_duration=extra_duration)
    db.session.add(new_addon)
    db.session.commit()

    flash(f'Treatment add-on option "{name}" cataloged into menu configuration metrics.', 'success')
    return redirect(url_for('addon.index'))