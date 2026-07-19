# routes/dashboard.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.product import Product
# Note: We will import actual models (Appointment, Product, Invoice) as we build them.
# For now, we calculate structural metrics to populate our metrics framework.

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    low_stock_count= Product.query.filter(Product.stock< Product.min_stock).count()
    # Placeholder aggregated stats that will connect to our database models in later modules
    metrics = {
        'today_appointments': 0,
        'today_income': 0.00,
        'monthly_income': 0.00,
        'available_barbers': 0,
        'pending_payments': 0,
        'low_stock_alerts': low_stock_count
    }
    
    # Context summary highlighting user specific operational details
    user_context = {
        'name': current_user.name,
        'role': current_user.role
    }

    return render_template('dashboard.html', metrics=metrics, user=user_context)