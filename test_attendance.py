# test_attendance.py
import unittest
from datetime import datetime, timedelta, timezone
from app import create_app, db
from models.user import User
from models.employee import Employee
from models.attendance import Attendance
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class AttendanceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Admin Boss', email='boss@barber.com', role='Admin')
        self.user.set_password('boss123')
        
        self.emp = Employee(name='Barber Bob', phone='555-4000', salary=1500.0)
        db.session.add(self.user)
        db.session.add(self.emp)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'boss@barber.com', 'password': 'boss123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_attendance_time_calculations_and_safeguards(self):
        """Test that clocking entry calculations compute decimal elapsed shift metrics smoothly."""
        start_time = datetime.now(timezone.utc) - timedelta(hours=8) # Emulate an 8-hour shift
        
        # 1. Manually add an attendance record
        log = Attendance(
            employee_id=self.emp.id,
            date=datetime.now(timezone.utc).date(),
            check_in=start_time,
            check_out=datetime.now(timezone.utc)
        )
        log.calculate_hours()
        db.session.add(log)
        db.session.commit()

        # Check that internal elapsed runtime formulas register a solid 8.0 hours
        fetched = Attendance.query.first()
        self.assertEqual(fetched.working_hours, 8.0)

        # 2. Test operational business logic: Block duplicate shift creation posts for today
        duplicate_response = self.client.post('/attendance/check-in', data={
            'employee_id': self.emp.id
        }, follow_redirects=True)
        
        self.assertIn(b"already clocked in for today", duplicate_response.data)

if __name__ == '__main__':
    unittest.main()