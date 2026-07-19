# test_auth.py
import unittest
from app import create_app, db
from models.user import User
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Run tests inside RAM to preserve system disk

class AuthenticationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing_and_verification(self):
        u = User(name='Alex Barber', email='alex@shop.com', role='Admin')
        u.set_password('super-secret-pass-2026')
        
        self.assertFalse(u.password_hash == 'super-secret-pass-2026')
        self.assertTrue(u.check_password('super-secret-pass-2026'))
        self.assertFalse(u.check_password('wrong-password'))

    def test_user_roles_and_defaults(self):
        u = User(name='Sam Cut', email='sam@shop.com')
        u.set_password('password123')
        db.session.add(u)
        db.session.commit()
        
        fetched = User.query.filter_by(email='sam@shop.com').first()
        self.assertEqual(fetched.role, 'Barber') # Default validation
        self.assertTrue(fetched.status)

if __name__ == '__main__':
    unittest.main()