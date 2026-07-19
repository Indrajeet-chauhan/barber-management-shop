# routes/inventory.py
import os  # <-- Required for path tracking tools
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required
from database import db
from models.product import Product
from services.barcode_service import BarcodeService

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory', methods=['GET'])
@login_required
def index():
    """List all stock products in the inventory registry system."""
    products = Product.query.order_by(Product.name.asc()).all()
    return render_template('inventory/index.html', products=products)

@inventory_bp.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a brand new item variant to the warehouse inventory roster."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', 'Retail').strip()
        barcode_code = request.form.get('barcode_code', '').strip() or None
        purchase_price = float(request.form.get('purchase_price', 0.0))
        selling_price = float(request.form.get('selling_price', 0.0))
        stock = int(request.form.get('stock', 0))
        min_stock = int(request.form.get('min_stock', 5))
        supplier = request.form.get('supplier', '').strip() or None

        if Product.query.filter_by(name=name).first():
            flash('An inventory item with this exact description name already exists.', 'danger')
            return redirect(url_for('inventory.add'))
            
        if barcode_code and Product.query.filter_by(barcode_code=barcode_code).first():
            flash('A product with this barcode code sequence already exists.', 'danger')
            return redirect(url_for('inventory.add'))

        new_product = Product(
            name=name, category=category, barcode_code=barcode_code,
            purchase_price=purchase_price, selling_price=selling_price, 
            stock=stock, min_stock=min_stock, supplier=supplier
        )
        db.session.add(new_product)
        db.session.commit()
        
        flash(f'Product "{name}" cataloged into inventory.', 'success')
        return redirect(url_for('inventory.index'))

    return render_template('inventory/add.html')

@inventory_bp.route('/inventory/restock/<int:id>', methods=['POST'])
@login_required
def restock(id):
    """Adjust inventory stock levels upward when shipments are received."""
    product = Product.query.get_or_404(id)
    quantity = int(request.form.get('quantity', 0))
    
    if quantity <= 0:
        flash('Restock value entry adjustments must be positive integers.', 'warning')
        return redirect(url_for('inventory.index'))

    product.stock += quantity
    db.session.commit()
    
    flash(f'Updated stock counts for {product.name}. New total: {product.stock}', 'success')
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/inventory/generate-barcode/<int:id>', methods=['POST'])
@login_required
def generate_barcode(id):
    """Triggers generation of visual image file barcode labels for catalog items."""
    product = Product.query.get_or_404(id)
    
    if not product.barcode_code:
        flash('Cannot render graphical label asset without assigned item code digits.', 'warning')
        return redirect(url_for('inventory.index'))

    # Route directory path targeting the web server's public static folder structures
    storage_path = os.path.join(current_app.root_path, 'static', 'barcodes')
    
    # Process computational rendering out via our isolated backend service block
    filename = BarcodeService.generate_ean13_barcode_image(product.barcode_code, storage_path)
    
    flash(f'Graphical barcode asset rendered successfully as: {filename}', 'success')
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/api/barcode/scan/<string:code>', methods=['GET'])
@login_required
def api_scan_lookup(code):
    """High-speed JSON API lookup endpoint matching scanner hardware inputs."""
    product = Product.query.filter_by(barcode_code=code).first()
    
    if not product:
        return jsonify({'success': False, 'message': 'Product item not found in catalog logs.'}), 404
        
    return jsonify({
        'success': True,
        'product_id': product.id,
        'name': product.name,
        'price': product.selling_price,
        'current_stock': product.stock
    })