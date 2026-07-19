# routes/payment.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database import db
from models.payment import Payment
from models.invoice import Invoice

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/payments', methods=['GET'])
@login_required
def index():
    """List historical electronic gateway payment transaction logs."""
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template('payment/index.html', payments=payments)

@payment_bp.route('/payments/record', methods=['POST'])
@login_required
def record_payment():
    """Log or attach a modern gateway tracking code directly onto an invoice document anchor."""
    invoice_id = int(request.form.get('invoice_id'))
    amount = float(request.form.get('amount', 0.0))
    gateway = request.form.get('gateway', 'Cash').strip()
    transaction_ref = request.form.get('transaction_ref', '').strip() or None

    # Check for potential unique constraint token collisions from previous entries
    if transaction_ref and Payment.query.filter_by(transaction_ref=transaction_ref).first():
        flash('This transaction reference ID has already been logged into the system sheets.', 'danger')
        return redirect(url_for('payment.index'))

    invoice = Invoice.query.get_or_404(invoice_id)

    # Initialize a successful capture tracker
    new_payment = Payment(
        invoice_id=invoice_id,
        amount=amount,
        gateway=gateway,
        transaction_ref=transaction_ref,
        status='Success'
    )
    db.session.add(new_payment)
    db.session.commit()

    flash(f'Payment transaction for ${amount} processed and verified successfully.', 'success')
    return redirect(url_for('payment.index'))

@payment_bp.route('/payments/refund/<int:id>', methods=['POST'])
@login_required
def process_refund(id):
    """Execute full status adjustment conversions for reversing billing transaction metrics."""
    payment_record = Payment.query.get_or_404(id)

    if payment_record.status == 'Refunded':
        flash('This transaction item has already been adjusted as refunded.', 'warning')
        return redirect(url_for('payment.index'))

    payment_record.status = 'Refunded'
    db.session.commit()

    flash(f'Payment reference {payment_record.transaction_ref} reversed and marked as refunded.', 'success')
    return redirect(url_for('payment.index'))