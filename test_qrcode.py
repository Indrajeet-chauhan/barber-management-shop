# test_qrcode.py
import unittest
import os
import shutil
from app import create_app, db
from models.user import User
from models.customer import Customer
from models.membership import MembershipTier, CustomerMembership
from config import Config
from datetime import datetime, timedelta, timezone

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class QRCodeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Membership Manager', email='member@barber.com', role='Admin')
        self.user.set_password('member123')
        
        self.cust = Customer(name='Lionel Messi', phone='555-1010')
        self.tier = MembershipTier(name='Platinum VIP Club', monthly_fee=99.0, discount_percentage=25.0)
        
        db.session.add(self.user)
        db.session.add(self.cust)
        db.session.add(self.tier)
        db.session.commit()

        # Seed an active sub row anchor directly onto customer profile
        self.sub = CustomerMembership(
            customer_id=self.cust.id,
            tier_id=self.tier.id,
            start_date=datetime.now(timezone.utc).date(),
            next_renewal=datetime.now(timezone.utc).date() + timedelta(days=30),
            status='Active'
        )
        db.session.add(self.sub)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'member@barber.com', 'password': 'member123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        # Strip away local testing folder structures rendered during execution pass
        test_dir = os.path.join(self.app.root_path, 'static', 'qrcodes')
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

    def test_membership_qr_card_generation(self):
        """Test that matrix qr graphic formats parse out to server hard drives reliably."""
        # 1. Fire generation query POST call through active router
        response = self.client.post(f'/memberships/generate-qr/{self.sub.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # 2. Confirm layout checks hit successfully
        self.assertIn(b"rendered successfully", response.data)
        
        # 3. Double check filesystem asset initialization directly on path bounds
        expected_filename = f"member_qr_{self.cust.id}.png"
        full_path = os.path.join(self.app.root_path, 'static', 'qrcodes', expected_filename)
        self.assertTrue(os.path.exists(full_path))

if __name__ == '__main__':
    unittest.main()