# test_employee.py
import unittest
from datetime import date
from app import create_app, db
from models.user import User
from models.employee import Employee
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class EmployeeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed authenticated system layer access credentials
        self.user = User(name='Manager User', email='manager@barber.com', role='Manager')
        self.user.set_password('manager123')
        db.session.add(self.user)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'manager@barber.com', 'password': 'manager123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_employee_creation_and_attributes(self):
        """Test that staff registration details pass engine constraints seamlessly."""
        emp = Employee(
            name='Master Cutter', 
            phone='+999888777', 
            salary=2500.0, 
            commission_rate=15.0,
            role='Barber'
        )
        db.session.add(emp)
        db.session.commit()
        
        fetched = Employee.query.filter_by(phone='+999888777').first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.salary, 2500.0)
        self.assertEqual(fetched.commission_rate, 15.0)
        self.assertTrue(fetched.status)

if __name__ == '__main__':
    unittest.main()