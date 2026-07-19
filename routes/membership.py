# routes/membership.py
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request,current_app
from flask_login import login_required
from database import db
from models.membership import MembershipTier, CustomerMembership
from models.customer import Customer
from datetime import datetime, timedelta, timezone
from services.qrcode_service import QRCodeService

membership_bp = Blueprint('membership', __name__)

@membership_bp.route('/memberships/generate-qr/<int:id>', methods=['POST'])
@login_required
def generate_qr(id):
    """Triggers generation of digital membership QR codes for scanner lookups."""
    sub_profile = CustomerMembership.query.get_or_404(id)

    # Route folder location matching our public web asset roots
    storage_path = os.path.join(current_app.root_path, 'static', 'qrcodes')

    # Execute generation through our backend engine service layer
    filename = QRCodeService.generate_membership_qr_code(
        customer_id=sub_profile.customer_id,
        membership_identifier=sub_profile.tier.name.upper().replace(" ", "_"),
        output_directory=storage_path
    )

    flash(f'Digital membership QR card rendered successfully: {filename}', 'success')
    return redirect(url_for('membership.index'))


@membership_bp.route('/memberships', methods=['GET'])
@login_required
def index():
    """List out membership tiers and customer subscription registers."""
    tiers = MembershipTier.query.filter_by(status=True).all()
    subscriptions = CustomerMembership.query.all()
    return render_template('membership/index.html', tiers=tiers, subscriptions=subscriptions)

@membership_bp.route('/memberships/tier/add', methods=['POST'])
@login_required
def add_tier():
    """Create a brand new structural membership program tier tier variant."""
    name = request.form.get('name', '').strip()
    fee = float(request.form.get('monthly_fee', 0.0))
    discount = float(request.form.get('discount_percentage', 0.0))
    benefits = request.form.get('benefits', '').strip() or None

    if MembershipTier.query.filter_by(name=name).first():
        flash('A membership program level tier with that matching name already exists.', 'danger')
        return redirect(url_for('membership.index'))

    new_tier = MembershipTier(name=name, monthly_fee=fee, discount_percentage=discount, benefits=benefits)
    db.session.add(new_tier)
    db.session.commit()

    flash(f'Membership program "{name}" cataloged successfully.', 'success')
    return redirect(url_for('membership.index'))

@membership_bp.route('/memberships/subscribe', methods=['POST'])
@login_required
def subscribe_customer():
    """Assign a customer profile to an active membership sub-tier layer."""
    customer_id = int(request.form.get('customer_id'))
    tier_id = int(request.form.get('tier_id'))
    
    # Business rule safeguard: clear or catch pre-existing active sub accounts
    existing = CustomerMembership.query.filter_by(customer_id=customer_id).first()
    if existing and existing.status == 'Active':
        flash('Customer profile already holds an active recurring program assignment.', 'warning')
        return redirect(url_for('membership.index'))

    start_date = datetime.now(timezone.utc).date()
    # Compute next automated cycle deadline target date (30 calendar day intervals)
    next_renewal = start_date + timedelta(days=30)

    # Overwrite or build a clean sub record block
    if existing:
        existing.tier_id = tier_id
        existing.start_date = start_date
        existing.next_renewal = next_renewal
        existing.status = 'Active'
    else:
        new_sub = CustomerMembership(
            customer_id=customer_id, tier_id=tier_id,
            start_date=start_date, next_renewal=next_renewal
        )
        db.session.add(new_sub)

    db.session.commit()
    flash('Customer account added to the selected subscription program tier successfully.', 'success')
    return redirect(url_for('membership.index'))