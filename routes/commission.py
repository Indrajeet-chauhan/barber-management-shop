# routes/commission.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database import db
from models.commission import CommissionLedger
from models.employee import Employee
from models.invoice import InvoiceItem

commission_bp = Blueprint('commission', __name__)

@commission_bp.route('/commissions', methods=['GET'])
@login_required
def index():
    """List out historical staff performance split commissions logs."""
    ledger_entries = CommissionLedger.query.order_by(CommissionLedger.created_at.desc()).all()
    
    # Aggregate total pending payout balances dynamically for summary analytics indicators
    total_unpaid = sum(entry.commission_payout for entry in ledger_entries)
    
    return render_template('commission/index.html', entries=ledger_entries, total_unpaid=round(total_unpaid, 2))

@commission_bp.route('/commissions/log', methods=['POST'])
@login_required
def log_split_commission():
    """Programmatically logs a performance cut line item entry down inside the ledger schema."""
    employee_id = int(request.form.get('employee_id'))
    invoice_item_id = int(request.form.get('invoice_item_id'))
    net_sales_amount = float(request.form.get('net_sales_amount', 0.0))
    item_type = request.form.get('item_type', 'Service').strip()

    emp = Employee.query.get_or_404(employee_id)
    
    # Enforce standard commission parameters tied onto core employee profile blocks
    rate_to_apply = emp.commission_rate

    new_entry = CommissionLedger(
        employee_id=employee_id,
        invoice_item_id=invoice_item_id,
        net_sales_amount=net_sales_amount,
        commission_rate=rate_to_apply,
        item_type=item_type
    )
    new_entry.calculate_payout()
    
    db.session.add(new_entry)
    db.session.commit()

    flash(f'Performance commission split of ${new_entry.commission_payout} logged for {emp.name}.', 'success')
    return redirect(url_for('commission.index'))