# test_appointment.py
import unittest
from datetime import date, time
from app import create_app, db
from models.user import User
from models.customer import Customer
from models.employee import Employee
from models.appointment import Appointment
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class AppointmentTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # 1. Seed Authenticated System Session Account
        self.user = User(name='Scheduler User', email='sched@barber.com', role='Receptionist')
        self.user.set_password('reception123')
        db.session.add(self.user)
        
        # 2. Seed a mock Customer and Employee profile for relational mapping dependencies
        self.cust = Customer(name='Alice Smith', phone='555-0199')
        self.emp = Employee(name='Jack Scissors', phone='555-0200', salary=2000.0)
        
        db.session.add(self.cust)
        db.session.add(self.emp)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'sched@barber.com', 'password': 'reception123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_appointment_booking_and_conflict_handling(self):
        """Test that appointment engine hooks work perfectly and catch scheduling conflicts."""
        # Book an initial slot
        apt1 = Appointment(
            customer_id=self.cust.id,
            employee_id=self.emp.id,
            date=date(2026, 8, 20),
            time=time(14, 0),
            service_name='Classic Haircut'
        )
        db.session.add(apt1)
        db.session.commit()
        
        # Verify the relational bindings pull correctly
        fetched = Appointment.query.first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.customer.name, 'Alice Smith')
        
        # Attempt to double book that exact barber slot
        response = self.client.post('/appointments/book', data={
            'customer_id': self.cust.id,
            'employee_id': self.emp.id,
            'service_name': 'Beard Trim',
            'date': '2026-08-20',
            'time': '14:00'
        }, follow_redirects=True)
        
        # Confirm that the mock engine outputs the rendering checkpoint target perfectly
        self.assertIn(b"Scheduling Conflict", response.data)

if __name__ == '__main__':
    unittest.main()