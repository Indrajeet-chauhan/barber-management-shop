# test_loyalty.py
import unittest
from app import create_app, db
from models.user import User
from models.customer import Customer
from models.loyalty import LoyaltyAccount, LoyaltyTransaction
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class LoyaltyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Cashier Desk', email='desk@barber.com', role='Receptionist')
        self.user.set_password('deskpass123')
        
        self.cust = Customer(name='Zinedine Zidane', phone='555-0012')
        db.session.add(self.user)
        db.session.add(self.cust)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'desk@barber.com', 'password': 'deskpass123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_loyalty_point_accrual_and_redemption_safeguards(self):
        """Test that rewards add up accurately and reject insufficient requests."""
        # 1. Trigger point accrual via HTTP routing
        response = self.client.post('/loyalty/earn', data={
            'customer_id': self.cust.id,
            'amount_spent': '150.50'
        }, follow_redirects=True)

        account = LoyaltyAccount.query.filter_by(customer_id=self.cust.id).first()
        self.assertIsNotNone(account)
        self.assertEqual(account.points_balance, 150) # Int cast verify ($150 spend = 150 pts)

        # Confirm audit transaction row entry
        tx_earn = LoyaltyTransaction.query.filter_by(transaction_type='Earned').first()
        self.assertEqual(tx_earn.points, 150)

        # 2. Test redemption processing subtraction balance checks
        self.client.post('/loyalty/redeem', data={
            'customer_id': self.cust.id,
            'points': '50'
        }, follow_redirects=True)

        self.assertEqual(account.points_balance, 100) # 150 - 50 = 100 points balance

        # 3. Test guard block: Requesting more points than held should trigger an error message
        err_response = self.client.post('/loyalty/redeem', data={
            'customer_id': self.cust.id,
            'points': '500'
        }, follow_redirects=True)
        
        self.assertIn(b"Insufficient point balance sheet holdings", err_response.data)

if __name__ == '__main__':
    unittest.main()