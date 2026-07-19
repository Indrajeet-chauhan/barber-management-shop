# test_commission.py
import unittest
from app import create_app, db
from models.user import User
from models.employee import Employee
from models.invoice import Invoice, InvoiceItem
from models.commission import CommissionLedger
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class CommissionTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Lead Accountant', email='finance@barber.com', role='Admin')
        self.user.set_password('ledgerpass123')
        
        # Seed barber profile with a 20% commission split contract setup
        self.emp = Employee(name='Barber Fernando', phone='555-4321', salary=1500.0, commission_rate=20.0)
        
        # Seed an invoice line item context anchor block
        self.inv = Invoice(invoice_number='INV-SPLIT-99', subtotal=60.0, total=60.0)
        self.item = InvoiceItem(item_name='Classic Scissor Cut', quantity=1, unit_price=60.0, total_price=60.0)
        self.inv.items.append(self.item)

        db.session.add(self.user)
        db.session.add(self.emp)
        db.session.add(self.inv)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'finance@barber.com', 'password': 'ledgerpass123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_commission_split_calculation_pipeline(self):
        """Test that line item commissions extract and compute payout fractions flawlessly."""
        # 1. Post a commission log action command via router endpoint paths
        response = self.client.post('/commissions/log', data={
            'employee_id': self.emp.id,
            'invoice_item_id': self.item.id,
            'net_sales_amount': '60.0',
            'item_type': 'Service'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Performance commission split", response.data)

        # 2. Check Math Operations:
        # Net collected line value = $60.00
        # Contract rate = 20%
        # Payout total = 60 * 0.20 = $12.00
        ledger_row = CommissionLedger.query.first()
        self.assertIsNotNone(ledger_row)
        self.assertEqual(ledger_row.commission_payout, 12.0)
        self.assertEqual(ledger_row.employee.name, 'Barber Fernando')

if __name__ == '__main__':
    unittest.main()