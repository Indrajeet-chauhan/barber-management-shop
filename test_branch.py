# test_branch.py
import unittest
from app import create_app, db
from models.user import User
from models.branch import Branch
from models.employee import Employee
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class BranchTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Regional Supervisor', email='region@barber.com', role='Admin')
        self.user.set_password('regionpass123')
        db.session.add(self.user)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'region@barber.com', 'password': 'regionpass123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_branch_onboarding_and_staff_allocation_logic(self):
        """Test that branch models map tracking fields cleanly and intercept errors."""
        # 1. Post a new location via HTTP router endpoint calls
        response = self.client.post('/branches/add', data={
            'name': 'North Avenue Galleria',
            'address': '742 Evergreen Terrace Suite B',
            'phone': '555-9876'
        }, follow_redirects=True)

        # Confirm database holds the branch entry correctly
        loc = Branch.query.filter_by(name='North Avenue Galleria').first()
        self.assertIsNotNone(loc)
        self.assertEqual(loc.address, '742 Evergreen Terrace Suite B')

        # 2. Test staff relational foreign key mapping boundaries
        emp = Employee(name='Barber Eric', phone='555-0099', salary=1200.0, branch_id=loc.id)
        db.session.add(emp)
        db.session.commit()

        self.assertEqual(len(loc.staff_roster), 1)
        self.assertEqual(loc.staff_roster[0].name, 'Barber Eric')

        # 3. Block unique collision descriptor entries
        dup_response = self.client.post('/branches/add', data={
            'name': 'North Avenue Galleria',
            'address': 'Different Street Name Check'
        }, follow_redirects=True)
        self.assertIn(b"matching name description already exists", dup_response.data)

if __name__ == '__main__':
    unittest.main()