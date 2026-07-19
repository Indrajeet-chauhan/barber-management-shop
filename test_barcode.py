# test_barcode.py
import unittest
import os
import shutil
from app import create_app, db
from models.user import User
from models.product import Product
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class BarcodeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name='Cashier Scan Tech', email='scan@barber.com', role='Receptionist')
        self.user.set_password('scan123')
        
        # Seed an item with an exactly valid 12-digit structural string sequence setup
        self.p1 = Product(name='Premium Styling Pomade', purchase_price=12.0, selling_price=25.0, stock=50, barcode_code='123456789012')
        
        db.session.add(self.user)
        db.session.add(self.p1)
        db.session.commit()
        
        self.client.post('/login', data={'email': 'scan@barber.com', 'password': 'scan123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        # Clean up any test directory image artifacts rendered on disk
        test_dir = os.path.join(self.app.root_path, 'static', 'barcodes')
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

    def test_barcode_generation_and_scanning_lookup_api(self):
        """Test that graphical assets render and high-speed scan endpoints respond cleanly."""
        # 1. Trigger the graphic barcode generator script via endpoint post execution routes
        gen_response = self.client.post(f'/inventory/generate-barcode/{self.p1.id}', follow_redirects=True)
        self.assertEqual(gen_response.status_code, 200)
        self.assertIn(b"rendered successfully", gen_response.data)

        # 2. Simulate hardware scanner gun data beam firing against lookup API routes
        api_response = self.client.get('/api/barcode/scan/123456789012')
        self.assertEqual(api_response.status_code, 200)
        
        json_data = api_response.get_json()
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['name'], 'Premium Styling Pomade')
        self.assertEqual(json_data['price'], 25.0)

        # 3. Test verification lookup shield fails gracefully when incorrect codes are read
        bad_response = self.client.get('/api/barcode/scan/000000000000')
        self.assertEqual(bad_response.status_code, 404)

if __name__ == '__main__':
    unittest.main()