# test_reports.py
import unittest
from datetime import date, datetime
from app import create_app, db
from models.user import User
from models.invoice import Invoice, InvoiceItem
from models.product import Product
from services.report_service import ReportService
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ReportsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Executive Owner', email='owner@barber.com', role='Admin')
        self.user.set_password('boss123')
        db.session.add(self.user)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'owner@barber.com', 'password': 'boss123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_report_service_matrix_calculations(self):
        """Test that analytics engine algorithms compute and pull metrics cleanly."""
        # 1. Seed invoice records matching today's calendar window
        inv1 = Invoice(invoice_number='INV-REP-1', subtotal=100.0, tax=10.0, discount=0.0, total=110.0, created_at=datetime.combine(date.today(), datetime.min.time()))
        item1 = InvoiceItem(item_name='Luxury Grooming Trim', quantity=2, unit_price=50.0, total_price=100.0)
        inv1.items.append(item1)

        # 2. Seed an inventory alert state item variant
        p1 = Product(name='Beard Conditioning Gel', stock=1, min_stock=5)

        db.session.add(inv1)
        db.session.add(p1)
        db.session.commit()

        # Run computational diagnostic execution pipelines directly from the service layer
        matrix = ReportService.generate_management_dashboard_matrix(target_date=date.today())

        # Verify performance metric parameters output precisely matching math configurations
        self.assertEqual(matrix['today_revenue'], 110.0)
        self.assertEqual(matrix['monthly_revenue'], 110.0)
        self.assertEqual(matrix['inventory_alerts'], 1)
        self.assertEqual(matrix['top_services'][0]['name'], 'Luxury Grooming Trim')

        # Confirm the actual routing gateway processes successfully
        response = self.client.get('/reports/analytics')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()