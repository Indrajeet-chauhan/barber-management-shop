# routes/system.py
import csv
import io
from flask import Blueprint, Response, flash, redirect, url_for, render_template
from flask_login import login_required
from models.customer import Customer
from models.invoice import Invoice
from models.product import Product

system_bp = Blueprint('system', __name__)

@system_bp.route('/system/tools', methods=['GET'])
@login_required
def index():
    """Renders administrative maintenance and data engine utility options."""
    return render_template('system/tools.html')

@system_bp.route('/system/export/customers', methods=['GET'])
@login_required
def export_customers_csv():
    """Compiles customer profile tracking cards into a standard CSV data stream."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write column descriptors
    writer.writerow(['Customer ID', 'Full Name', 'Phone Line', 'Email Address'])
    
    records = Customer.query.order_by(Customer.id.asc()).all()
    for row in records:
        writer.writerow([row.id, row.name, row.phone, row.email or 'N/A'])
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=barber_customers_backup.csv"}
    )

@system_bp.route('/system/export/invoices', methods=['GET'])
@login_required
def export_invoices_csv():
    """Compiles core commercial sales tracking ledger arrays into a flat file stream."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Invoice Ref', 'Subtotal', 'Tax', 'Discount', 'Grand Total', 'Payment Mode', 'Timestamp'])
    
    records = Invoice.query.order_by(Invoice.created_at.desc()).all()
    for row in records:
        writer.writerow([row.invoice_number, row.subtotal, row.tax, row.discount, row.total, row.payment_mode, row.created_at])
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=financial_sales_ledger.csv"}
    )