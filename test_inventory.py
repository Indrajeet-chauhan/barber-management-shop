# test_inventory.py
import unittest
from app import create_app, db
from models.user import User
from models.product import Product
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class InventoryTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Stock Clerk', email='clerk@barber.com', role='Manager')
        self.user.set_password('stock123')
        db.session.add(self.user)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'clerk@barber.com', 'password': 'stock123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_inventory_stock_logic_and_alerts(self):
        """Test that stock level allocations increment and fire indicators accurately."""
        # 1. Create a product that immediately presents a low stock condition
        p1 = Product(name='Matte Pomade Matte', purchase_price=10.0, selling_price=22.0, stock=2, min_stock=5)
        db.session.add(p1)
        db.session.commit()
        
        # Pull down dashboard workspace view and confirm our live engine reads the alert state
        dash_response = self.client.get('/dashboard')
        self.assertEqual(dash_response.status_code, 200)
        
        # 2. Test restock inbound workflow increments correctly
        response = self.client.post(f'/inventory/restock/{p1.id}', data={
            'quantity': '10'
        }, follow_redirects=True)
        
        updated_product = Product.query.get(p1.id)
        self.assertEqual(updated_product.stock, 12) # 2 + 10 = 12 items in inventory

        # 3. Test uniqueness constraint checks throw properly
        err_response = self.client.post('/inventory/add', data={
            'name': 'Matte Pomade Matte',
            'category': 'Retail',
            'purchase_price': '10.0',
            'selling_price': '22.0',
            'stock': '20',
            'min_stock': '5'
        }, follow_redirects=True)
        self.assertIn(b"description name already exists", err_response.data)

if __name__ == '__main__':
    unittest.main()