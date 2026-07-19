# test_customer.py
import unittest
from datetime import date
from app import create_app, db
from models.user import User
from models.customer import Customer
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class CustomerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed admin session credentials
        self.user = User(name='Admin Staff', email='staff@barber.com', role='Receptionist')
        self.user.set_password('reception123')
        db.session.add(self.user)
        db.session.commit()
        
        # Log in the mock client session
        self.client.post('/login', data={'email': 'staff@barber.com', 'password': 'reception123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_customer_crud_operations(self):
        """Test that customer info records cleanly pass validation rules."""
        # 1. Test Create
        c = Customer(name='John Doe', phone='+1234567890', birthday=date(1995, 5, 20), notes='Prefers low fade')
        db.session.add(c)
        db.session.commit()
        
        fetched = Customer.query.filter_by(phone='+1234567890').first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, 'John Doe')
        
        # 2. Test Update
        fetched.name = 'Johnathan Doe'
        db.session.commit()
        
        updated = Customer.query.get(fetched.id)
        self.assertEqual(updated.name, 'Johnathan Doe')

if __name__ == '__main__':
    unittest.main()