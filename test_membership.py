# test_membership.py
import unittest
from datetime import datetime, timezone
from app import create_app, db
from models.user import User
from models.customer import Customer
from models.membership import MembershipTier, CustomerMembership
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class MembershipTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Admin Desk', email='desk@barber.com', role='Admin')
        self.user.set_password('deskpass123')
        
        self.cust = Customer(name='David Beckham', phone='555-8000')
        db.session.add(self.user)
        db.session.add(self.cust)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'desk@barber.com', 'password': 'deskpass123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_membership_tier_creation_and_subscription_guards(self):
        """Test that subscription profiles initialize properly and capture duplicate bounds."""
        # 1. Manually build a structural discount tier
        tier = MembershipTier(name='Gold VIP Club', monthly_fee=50.0, discount_percentage=20.0)
        db.session.add(tier)
        db.session.commit()

        # 2. Subscribe user via endpoint POST action routing
        response = self.client.post('/memberships/subscribe', data={
            'customer_id': self.cust.id,
            'tier_id': tier.id
        }, follow_redirects=True)

        # Assert database configuration reflects tier status maps
        sub = CustomerMembership.query.filter_by(customer_id=self.cust.id).first()
        self.assertIsNotNone(sub)
        self.assertEqual(sub.tier.name, 'Gold VIP Club')
        self.assertEqual(sub.status, 'Active')

        # 3. Verify engine blocks redundant enrollment check logs
        dup_response = self.client.post('/memberships/subscribe', data={
            'customer_id': self.cust.id,
            'tier_id': tier.id
        }, follow_redirects=True)
        
        self.assertIn(b"already holds an active recurring program", dup_response.data)

if __name__ == '__main__':
    unittest.main()