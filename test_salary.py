# test_salary.py
import unittest
from app import create_app, db
from models.user import User
from models.employee import Employee
from models.salary import Salary
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class SalaryTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Finance Admin', email='finance@barber.com', role='Admin')
        self.user.set_password('payday123')
        
        # Base employee profile with 15% commission rate setup
        self.emp = Employee(name='Barber Charlie', phone='555-7000', salary=2000.0, commission_rate=15.0)
        db.session.add(self.user)
        db.session.add(self.emp)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'finance@barber.com', 'password': 'payday123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_salary_payout_math_and_uniqueness(self):
        """Test that net values add up cleanly and protect against duplicate payments."""
        # 1. Post payroll calculation command metrics via route endpoint
        response = self.client.post('/salaries/process', data={
            'employee_id': self.emp.id,
            'pay_period': '2026-07',
            'bonus': '250.0',
            'deductions': '50.0'
        }, follow_redirects=True)

        # 2. Check Math Operations:
        # Base Salary = 2000.0
        # Commission = 15% of $1000 sales base = 150.0
        # Bonus = 250.0
        # Deductions = 50.0
        # Grand Net = (2000 + 150 + 250) - 50 = $2350.00
        slip = Salary.query.first()
        self.assertIsNotNone(slip)
        self.assertEqual(slip.net_salary, 2350.0)

        # 3. Confirm business engine locks out duplicate payouts for the same period
        dup_response = self.client.post('/salaries/process', data={
            'employee_id': self.emp.id,
            'pay_period': '2026-07',
            'bonus': '0',
            'deductions': '0'
        }, follow_redirects=True)
        self.assertIn(b"period already exists", dup_response.data)

if __name__ == '__main__':
    unittest.main()