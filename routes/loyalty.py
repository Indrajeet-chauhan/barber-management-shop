# routes/loyalty.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database import db
from models.loyalty import LoyaltyAccount, LoyaltyTransaction

loyalty_bp = Blueprint('loyalty', __name__)

@loyalty_bp.route('/loyalty', methods=['GET'])
@login_required
def index():
    """List customer point balances and historical ledger transactions."""
    accounts = LoyaltyAccount.query.all()
    transactions = LoyaltyTransaction.query.order_by(LoyaltyTransaction.created_at.desc()).all()
    return render_template('loyalty/index.html', accounts=accounts, transactions=transactions)

@loyalty_bp.route('/loyalty/earn', methods=['POST'])
@login_required
def earn_points():
    """Add points to a customer's account based on custom promotional spending rule hooks."""
    customer_id = int(request.form.get('customer_id'))
    amount_spent = float(request.form.get('amount_spent', 0.0))
    
    # Business logic rule formulation: $1 spent = 1 loyalty point compiled down to integer values
    points_to_add = int(amount_spent)
    
    if points_to_add <= 0:
        flash('Invalid spend amount entered.', 'warning')
        return redirect(url_for('loyalty.index'))

    # Retrieve or build a new loyalty account structure instantly
    account = LoyaltyAccount.query.filter_by(customer_id=customer_id).first()
    if not account:
        account = LoyaltyAccount(customer_id=customer_id, points_balance=0)
        db.session.add(account)

    account.points_balance += points_to_add
    
    # Append clear audit track log details
    tx = LoyaltyTransaction(
        customer_id=customer_id,
        transaction_type='Earned',
        points=points_to_add,
        description=f"Points accrued from checkout spend: ${amount_spent}"
    )
    db.session.add(tx)
    db.session.commit()

    flash(f'Successfully credited {points_to_add} points to customer record.', 'success')
    return redirect(url_for('loyalty.index'))

@loyalty_bp.route('/loyalty/redeem', methods=['POST'])
@login_required
def redeem_reward():
    """Deduct loyalty points from a balance sheet container for item redemption rewards."""
    customer_id = int(request.form.get('customer_id'))
    points_to_redeem = int(request.form.get('points', 0))

    account = LoyaltyAccount.query.filter_by(customer_id=customer_id).first()
    if not account or account.points_balance < points_to_redeem:
        flash('Insufficient point balance sheet holdings available for redemption processing.', 'danger')
        return redirect(url_for('loyalty.index'))

    account.points_balance -= points_to_redeem
    
    tx = LoyaltyTransaction(
        customer_id=customer_id,
        transaction_type='Redeemed',
        points=points_to_redeem,
        description="Points converted at checkout counter for custom rewards benefit reduction"
    )
    db.session.add(tx)
    db.session.commit()

    flash(f'Successfully processed reward redemption for {points_to_redeem} points.', 'success')
    return redirect(url_for('loyalty.index'))