# test_system.py
import unittest
from app import create_app, db
from models.user import User
from models.customer import Customer
from models.invoice import Invoice
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class SystemTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='System Systems Administrator', email='sysadmin@barber.com', role='Admin')
        self.user.set_password('rootpass123')
        
        # Seed test entities to confirm serialization streams process columns properly
        self.cust = Customer(name='Andrea Pirlo', phone='555-2121', email='pirlo@barber.com')
        self.inv = Invoice(invoice_number='INV-SYS-EXPORT-1', subtotal=40.0, total=40.0)
        
        db.session.add(self.user)
        db.session.add(self.cust)
        db.session.add(self.inv)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'sysadmin@barber.com', 'password': 'rootpass123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_csv_export_streaming_utilities(self):
        """Test that data records convert to downloadable tabular text elements cleanly."""
        # 1. Pull down the custom profile file backup stream container
        cust_response = self.client.get('/system/export/customers')
        self.assertEqual(cust_response.status_code, 200)
        self.assertEqual(cust_response.mimetype, 'text/csv')
        self.assertIn(b"Andrea Pirlo", cust_response.data)
        self.assertIn(b"Customer ID,Full Name", cust_response.data)

        # 2. Pull down the commercial sales ticket ledger table matrix
        inv_response = self.client.get('/system/export/invoices')
        self.assertEqual(inv_response.status_code, 200)
        self.assertEqual(inv_response.mimetype, 'text/csv')
        self.assertIn(b"INV-SYS-EXPORT-1", inv_response.data)
        self.assertIn(b"Invoice Ref,Subtotal", inv_response.data)

if __name__ == '__main__':
    unittest.main()