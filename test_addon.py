# test_addon.py
import unittest
from datetime import date, time
from app import create_app, db
from models.user import User
from models.customer import Customer
from models.employee import Employee
from models.appointment import Appointment
from models.addon import Addon
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class AddonTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Salon Stylist Director', email='director@barber.com', role='Admin')
        self.user.set_password('passdirect123')
        
        self.cust = Customer(name='Gareth Bale', phone='555-1122')
        self.emp = Employee(name='Jack Scissors', phone='555-0200', salary=2000.0)
        
        db.session.add(self.user)
        db.session.add(self.cust)
        db.session.add(self.emp)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'director@barber.com', 'password': 'passdirect123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_addon_cataloging_and_appointment_accumulation(self):
        """Test that upgrade treatments stack and compound chair time durations accurately."""
        # 1. Post a new upgrade selection via router endpoints
        response = self.client.post('/addons/add', data={
            'name': 'Charcoal Peel Mask Treatment',
            'price': '25.0',
            'extra_duration': '15'
        }, follow_redirects=True)

        # Confirm the data row writes perfectly
        add_item = Addon.query.filter_by(name='Charcoal Peel Mask Treatment').first()
        self.assertIsNotNone(add_item)
        self.assertEqual(add_item.extra_duration, 15)

        # 2. Assign the treat package bundle onto an active appointment row
        apt = Appointment(
            customer_id=self.cust.id,
            employee_id=self.emp.id,
            date=date(2026, 8, 20),
            time=time(10, 0),
            service_name='Standard Trim'
        )
        apt.addons.append(add_item)
        db.session.add(apt)
        db.session.commit()

        # Check that duration math calculations aggregate correctly: 30 base + 15 upgrade = 45 mins total
        self.assertEqual(apt.get_total_duration(base_duration=30), 45)

        # 3. Block unique collision descriptor entries
        dup_response = self.client.post('/addons/add', data={
            'name': 'Charcoal Peel Mask Treatment',
            'price': '30.0'
        }, follow_redirects=True)
        self.assertIn(b"treatment package variant with this matching name already exists", dup_response.data)

if __name__ == '__main__':
    unittest.main()