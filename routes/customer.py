# routes/customer.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database import db
from models.customer import Customer
from datetime import datetime

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customers', methods=['GET'])
@login_required
def index():
    """List all registered customers."""
    customers = Customer.query.order_by(Customer.name.asc()).all()
    return render_template('customers/index.html', customers=customers)

@customer_bp.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a brand new customer profile."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip() or None
        address = request.form.get('address', '').strip() or None
        notes = request.form.get('notes', '').strip() or None
        
        birthday_raw = request.form.get('birthday', '')
        birthday = None
        if birthday_raw:
            birthday = datetime.strptime(birthday_raw, '%Y-%m-%d').date()

        # Validate unique phone number constraint
        if Customer.query.filter_by(phone=phone).first():
            flash('A customer with this phone number already exists.', 'danger')
            return redirect(url_for('customer.add'))

        new_customer = Customer(
            name=name, phone=phone, email=email, 
            address=address, birthday=birthday, notes=notes
        )
        db.session.add(new_customer)
        db.session.commit()
        
        flash(f'Customer {name} added successfully!', 'success')
        return redirect(url_for('customer.index'))

    return render_template('customers/add.html')

@customer_bp.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Update an existing customer profile."""
    customer = Customer.query.get_or_404(id)
    
    if request.method == 'POST':
        customer.name = request.form.get('name', '').strip()
        customer.phone = request.form.get('phone', '').strip()
        customer.email = request.form.get('email', '').strip() or None
        customer.address = request.form.get('address', '').strip() or None
        customer.notes = request.form.get('notes', '').strip() or None
        
        birthday_raw = request.form.get('birthday', '')
        if birthday_raw:
            customer.birthday = datetime.strptime(birthday_raw, '%Y-%m-%d').date()
        else:
            customer.birthday = None

        db.session.commit()
        flash('Customer profile updated successfully.', 'success')
        return redirect(url_for('customer.index'))

    return render_template('customers/edit.html', customer=customer)