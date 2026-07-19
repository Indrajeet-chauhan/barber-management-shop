# test_billing.py
import unittest
from app import create_app, db
from models.user import User
from models.customer import Customer
from models.invoice import Invoice, InvoiceItem
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class BillingTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Cashier User', email='cashier@barber.com', role='Receptionist')
        self.user.set_password('cash123')
        
        self.cust = Customer(name='Bob Vance', phone='555-9000')
        db.session.add(self.user)
        db.session.add(self.cust)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'cashier@barber.com', 'password': 'cash123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_invoice_checkout_calculations_and_validation(self):
        """Test that line item additions parse financial totals accurately."""
        # Simulate a transaction checkout POST with two distinct line items
        response = self.client.post('/billing/checkout', data={
            'customer_id': self.cust.id,
            'payment_mode': 'UPI',
            'tax_rate': '10.0',   # 10% operational sales tax
            'discount': '5.0',    # $5.00 promotional discount
            'item_names[]': ['Premium Haircut', 'Beard Styling Oil'],
            'quantities[]': ['1', '2'],
            'unit_prices[]': ['40.0', '15.0'] # Subtotal = (1*40) + (2*15) = $70.00
        }, follow_redirects=True)

        # 1. Verify invoice saved correctly to database
        invoice = Invoice.query.first()
        self.assertIsNotNone(invoice)
        
        # 2. Check Math Operations:
        # Subtotal = 70.0
        # Tax = 10% of 70.0 = 7.0
        # Grand Total = (70.0 + 7.0) - 5.0 = 72.00
        self.assertEqual(invoice.subtotal, 70.0)
        self.assertEqual(invoice.tax, 7.0)
        self.assertEqual(invoice.discount, 5.0)
        self.assertEqual(invoice.total, 72.0)
        self.assertEqual(invoice.payment_mode, 'UPI')
        
        # 3. Check detailed items relational mapping integrity
        self.assertEqual(len(invoice.items), 2)
        self.assertEqual(invoice.items[0].item_name, 'Premium Haircut')
        self.assertEqual(invoice.items[1].total_price, 30.0)

        # 4. Test validation error catching for empty checkouts
        err_response = self.client.post('/billing/checkout', data={
            'customer_id': self.cust.id
        }, follow_redirects=True)
        self.assertIn(b"Cannot generate an invoice with zero line items", err_response.data)

if __name__ == '__main__':
    unittest.main()