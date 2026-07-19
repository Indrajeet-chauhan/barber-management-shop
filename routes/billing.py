# routes/billing.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from database import db
from models.invoice import Invoice, InvoiceItem
from models.customer import Customer
import time
import random

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/billing', methods=['GET'])
@login_required
def index():
    """List out historical financial invoices."""
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return render_template('billing/index.html', invoices=invoices)

@billing_bp.route('/billing/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Process a new service ticket sale transaction."""
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        customer_id = int(customer_id) if customer_id else None
        
        payment_mode = request.form.get('payment_mode', 'Cash')
        tax_rate = float(request.form.get('tax_rate', 0.0)) # Percentage value, e.g., 5.0 for 5%
        discount_amt = float(request.form.get('discount', 0.0))

        # Retrieve raw lists of submitted item items from the checkout grid form
        item_names = request.form.getlist('item_names[]')
        quantities = request.form.getlist('quantities[]')
        unit_prices = request.form.getlist('unit_prices[]')

        if not item_names:
            flash('Cannot generate an invoice with zero line items.', 'danger')
            return redirect(url_for('billing.checkout'))

        # 1. Compute Base Financial Subtotals
        subtotal = 0.0
        invoice_items_to_add = []

        for name, qty, price in zip(item_names, quantities, unit_prices):
            q = int(qty)
            p = float(price)
            item_total = q * p
            subtotal += item_total
            
            invoice_items_to_add.append(InvoiceItem(
                item_name=name, quantity=q, unit_price=p, total_price=item_total
            ))

        # 2. Calculate Final Compounded Totals
        calculated_tax = subtotal * (tax_rate / 100.0)
        final_total = (subtotal + calculated_tax) - discount_amt
        if final_total < 0: 
            final_total = 0.0

        # Generate a unique alpha-numeric sequential reference code
        unique_invoice_number = f"INV-{int(time.time())}-{random.randint(1000, 9999)}"

        # 3. Commit Transaction Blocks
        new_invoice = Invoice(
            invoice_number=unique_invoice_number,
            customer_id=customer_id,
            subtotal=subtotal,
            tax=calculated_tax,
            discount=discount_amt,
            total=final_total,
            payment_mode=payment_mode
        )

        for item in invoice_items_to_add:
            new_invoice.items.append(item)

        db.session.add(new_invoice)
        db.session.commit()

        flash(f'Invoice {unique_invoice_number} created successfully!', 'success')
        return redirect(url_for('billing.index'))

    customers = Customer.query.order_by(Customer.name.asc()).all()
    return render_template('billing/checkout.html', customers=customers)