# models/product.py
from database import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, default='Retail')
    
    # New Field Addition for Module 15: Unique 13-digit EAN/UPC identifier string
    barcode_code = db.Column(db.String(50), unique=True, nullable=True, index=True)
    
    purchase_price = db.Column(db.Float, nullable=False, default=0.0)
    selling_price = db.Column(db.Float, nullable=False, default=0.0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    min_stock = db.Column(db.Integer, nullable=False, default=5)
    supplier = db.Column(db.String(150), nullable=True)

    def __repr__(self):
        return f"<Product {self.name} - Barcode: {self.barcode_code}>"