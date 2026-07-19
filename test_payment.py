# test_payment.py
import unittest
from app import create_app, db
from models.user import User
from models.invoice import Invoice
from models.payment import Payment
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class PaymentTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Auditor Admin', email='audit@barber.com', role='Admin')
        self.user.set_password('auditpass123')
        
        # 1. Seed a mock invoice structural header anchor
        self.inv = Invoice(invoice_number='INV-TEST-100', subtotal=50.0, tax=5.0, discount=0.0, total=55.0, payment_mode='Card')
        
        db.session.add(self.user)
        db.session.add(self.inv)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'audit@barber.com', 'password': 'auditpass123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_payment_gateway_logging_and_refund_workflows(self):
        """Test that payment hashes map correctly to invoices and process state changes smoothly."""
        # 1. Post a new digital gateway payment tracking log configuration entry
        response = self.client.post('/payments/record', data={
            'invoice_id': self.inv.id,
            'amount': '55.0',
            'gateway': 'Stripe',
            'transaction_ref': 'ch_stripe_mock_hash_2026'
        }, follow_redirects=True)

        # Confirm the transaction is committed cleanly to the database ledger sheet matching parameters
        pmt = Payment.query.filter_by(transaction_ref='ch_stripe_mock_hash_2026').first()
        self.assertIsNotNone(pmt)
        self.assertEqual(pmt.amount, 55.0)
        self.assertEqual(pmt.status, 'Success')
        self.assertEqual(pmt.invoice.invoice_number, 'INV-TEST-100')

        # 2. Block unique token collision entries
        dup_response = self.client.post('/payments/record', data={
            'invoice_id': self.inv.id,
            'amount': '55.0',
            'gateway': 'Stripe',
            'transaction_ref': 'ch_stripe_mock_hash_2026'
        }, follow_redirects=True)
        self.assertIn(b"already been logged into the system", dup_response.data)

        # 3. Test active state adjustment refund workflows
        self.client.post(f'/payments/refund/{pmt.id}', follow_redirects=True)
        self.assertEqual(pmt.status, 'Refunded')

if __name__ == '__main__':
    unittest.main()