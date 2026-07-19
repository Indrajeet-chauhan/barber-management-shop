# test_service.py
import unittest
from app import create_app, db
from models.user import User
from models.service import Service
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Admin Manager', email='admin@barber.com', role='Admin')
        self.user.set_password('admin123')
        db.session.add(self.user)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'admin@barber.com', 'password': 'admin123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_service_catalog_addition_and_validation(self):
        """Test that menu options catalog correctly and catch duplicate names."""
        s = Service(name='Beard Trim Deluxe', price=35.0, duration=25, description='Hot towel shave combo')
        db.session.add(s)
        db.session.commit()
        
        fetched = Service.query.filter_by(name='Beard Trim Deluxe').first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.price, 35.0)
        self.assertEqual(fetched.duration, 25)
        self.assertTrue(fetched.status)

        # Attempt to inject duplicate name via routing context execution
        response = self.client.post('/services/add', data={
            'name': 'Beard Trim Deluxe',
            'price': '40.0',
            'duration': '30',
            'description': 'Duplicate Check Mock'
        }, follow_redirects=True)
        
        self.assertIn(b"matching name already exists", response.data)

if __name__ == '__main__':
    unittest.main()