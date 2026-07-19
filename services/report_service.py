# services/report_service.py
from database import db  # <-- This links the service to your database extension!
from sqlalchemy import func
from models.invoice import Invoice, InvoiceItem
from models.product import Product
from datetime import datetime, date

class ReportService:
    @staticmethod
    def generate_management_dashboard_matrix(target_date=None):
        """Aggregates all key performance indicators (KPIs) into a unified report."""
        if target_date is None:
            target_date = date.today()

        start_of_month = date(target_date.year, target_date.month, 1)

        # 1. Income aggregates
        today_sales = db.session.query(func.sum(Invoice.total)).filter(func.date(Invoice.created_at) == target_date).scalar() or 0.0
        month_sales = db.session.query(func.sum(Invoice.total)).filter(func.date(Invoice.created_at) >= start_of_month).scalar() or 0.0

        # 2. Top popularity item ranks
        popular_items = db.session.query(
            InvoiceItem.item_name,
            func.sum(InvoiceItem.quantity).label('qty')
        ).group_by(InvoiceItem.item_name).order_by(func.sum(InvoiceItem.quantity).desc()).limit(3).all()

        # 3. Low stock warning items count
        out_of_stock_count = Product.query.filter(Product.stock < Product.min_stock).count()

        return {
            'today_revenue': round(float(today_sales), 2),
            'monthly_revenue': round(float(month_sales), 2),
            'top_services': [{'name': item[0], 'count': int(item[1])} for item in popular_items],
            'inventory_alerts': out_of_stock_count
        }