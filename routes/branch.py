# routes/branch.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database import db
from models.branch import Branch
from models.employee import Employee

branch_bp = Blueprint('branch', __name__)

@branch_bp.route('/branches', methods=['GET'])
@login_required
def index():
    """List out physical branch shop storefront configurations."""
    branches = Branch.query.all()
    return render_template('branch/index.html', branches=branches)

@branch_bp.route('/branches/add', methods=['POST'])
@login_required
def add_branch():
    """Register a brand new corporate branch storefront hub anchor."""
    name = request.form.get('name', '').strip()
    address = request.form.get('address', '').strip()
    phone = request.form.get('phone', '').strip() or None

    if Branch.query.filter_by(name=name).first():
        flash('A branch storefront with this matching name description already exists.', 'danger')
        return redirect(url_for('branch.index'))

    new_branch = Branch(name=name, address=address, phone=phone)
    db.session.add(new_branch)
    db.session.commit()

    flash(f'Branch location "{name}" onboarded successfully.', 'success')
    return redirect(url_for('branch.index'))