# test_dashboard.py
import unittest
from app import create_app, db
from models.user import User
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class DashboardTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed an admin profile for test authentication states
        self.user = User(name='Boss Barber', email='owner@barber.com', role='Admin')
        self.user.set_password('securepass123')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_dashboard_requires_login(self):
        """Ensure unauthenticated traffic is blocked from reading the dashboard metrics."""
        response = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_authenticated_dashboard_access(self):
        """Ensure valid logged-in users can open the dashboard workspace."""
        # Log the user in via a POST request to our login system
        self.client.post('/login', data={
            'email': 'owner@barber.com',
            'password': 'securepass123'
        })
        
        # Pull dashboard view
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        # Verify the actual rendered template engine content components are outputting to client
        self.assertIn(b"Welcome Back, Boss Barber", response.data)

if __name__ == '__main__':
    unittest.main()