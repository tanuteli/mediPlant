# Supplier Routes for MediPlant

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.database import db
from app.models import Product, Order, Category, ProductImage, SupplierProfile, OrderItem, Review, User
from datetime import datetime, timedelta
from sqlalchemy import func, desc

supplier_bp = Blueprint('supplier', __name__, url_prefix='/supplier')

def supplier_required(f):
    """Decorator to require supplier access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_supplier():
            flash('Access denied. Supplier privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@supplier_bp.route('/dashboard')
@login_required
@supplier_required
def dashboard():
    """Supplier dashboard with comprehensive stats and recent activity"""
    # Calculate comprehensive stats
    stats = {
        'total_orders': Order.query.filter_by(supplier_id=current_user.id).count(),
        'total_products': Product.query.filter_by(supplier_id=current_user.id).count(),
        'total_revenue': db.session.query(func.sum(Order.total_amount))\
            .filter_by(supplier_id=current_user.id).scalar() or 0,
        'avg_rating': db.session.query(func.avg(Review.rating))\
            .join(Product).filter(Product.supplier_id == current_user.id).scalar() or 0
    }
    
    # Recent orders with detailed info
    recent_orders = Order.query.filter_by(supplier_id=current_user.id)\
        .order_by(desc(Order.created_at)).limit(5).all()
    
    # Format orders for template
    formatted_orders = []
    for order in recent_orders:
        formatted_orders.append({
            'id': order.id,
            'customer_name': order.user.name if order.user else 'Guest',
            'items_count': len(order.items) if hasattr(order, 'items') else 0,
            'total_amount': order.total_amount,
            'status': order.status,
            'created_at': order.created_at
        })
    
    # Low stock products (less than 20 units)
    low_stock_products = Product.query.filter_by(supplier_id=current_user.id)\
        .filter(Product.stock_quantity < 20).all()
    
    # Mock notifications for now - replace with actual notification system
    notifications = [
        {
            'title': 'Welcome to MediPlant!',
            'message': 'Complete your profile setup to start selling.',
            'created_at': datetime.now() - timedelta(minutes=10)
        },
        {
            'title': 'Inventory Alert',
            'message': 'Set up low stock alerts for your products.',
            'created_at': datetime.now() - timedelta(hours=2)
        }
    ]
    
    return render_template('supplier/dashboard.html', 
                         stats=stats,
                         recent_orders=formatted_orders,
                         notifications=notifications,
                         low_stock_products=low_stock_products)

@supplier_bp.route('/products')
@login_required
@supplier_required
def products():
    """View supplier's products (renamed from my_products for consistency)"""
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(supplier_id=current_user.id).order_by(
        desc(Product.created_at)
    ).paginate(page=page, per_page=20, error_out=False
    )
    return render_template('supplier/products.html', products=products)

@supplier_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@supplier_required
def add_product():
    """Add new product"""
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        category_id = request.form['category_id']
        description = request.form['description']
        price = float(request.form['price'])
        stock_quantity = int(request.form['stock_quantity'])
        
        # Create new product
        product = Product(
            name=name,
            category_id=category_id,
            supplier_id=current_user.id,
            description=description,
            base_price=price,
            stock_quantity=stock_quantity
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('supplier.my_products'))
    
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('supplier/add_product.html', categories=categories)

@supplier_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@supplier_required
def edit_product(product_id):
    """Edit product"""
    product = Product.query.filter_by(
        id=product_id, 
        supplier_id=current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.base_price = float(request.form['price'])
        product.stock_quantity = int(request.form['stock_quantity'])
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('supplier.my_products'))
    
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('supplier/edit_product.html', product=product, categories=categories)

@supplier_bp.route('/orders')
@login_required
@supplier_required
def orders():
    """View supplier's orders"""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(supplier_id=current_user.id).order_by(
        Order.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('supplier/orders.html', orders=orders)

@supplier_bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
@login_required
@supplier_required
def update_order_status(order_id):
    """Update order status"""
    order = Order.query.filter_by(
        id=order_id, 
        supplier_id=current_user.id
    ).first_or_404()
    
    new_status = request.form['status']
    order.status = new_status
    
    db.session.commit()
    flash('Order status updated successfully!', 'success')
    
    return redirect(url_for('supplier.orders'))

@supplier_bp.route('/analytics')
@login_required
@supplier_required
def analytics():
    """Enhanced supplier analytics with sales data"""
    # Get sales data for last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    try:
        sales_data = db.session.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('orders')
        ).filter(
            Order.supplier_id == current_user.id,
            Order.created_at >= thirty_days_ago
        ).group_by(func.date(Order.created_at)).all()
        
        # Top products by sales
        top_products = db.session.query(
            Product.name,
            func.sum(OrderItem.quantity).label('sold'),
            func.sum(OrderItem.subtotal).label('revenue')
        ).join(OrderItem).join(Order).filter(
            Product.supplier_id == current_user.id,
            Order.created_at >= thirty_days_ago
        ).group_by(Product.id).order_by(desc('sold')).limit(10).all()
        
    except Exception as e:
        # Fallback if tables don't exist or have issues
        sales_data = []
        top_products = []
    
    return render_template('supplier/analytics.html', 
                         sales_data=sales_data,
                         top_products=top_products)

@supplier_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@supplier_required
def profile():
    """Supplier profile management"""
    profile = SupplierProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        if not profile:
            profile = SupplierProfile(user_id=current_user.id)
        
        profile.business_name = request.form['business_name']
        profile.description = request.form['description']
        profile.address = request.form['address']
        profile.city = request.form['city']
        profile.state = request.form['state']
        profile.postal_code = request.form['postal_code']
        
        if not profile.id:
            db.session.add(profile)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('supplier.profile'))
    
    return render_template('supplier/profile.html', profile=profile)

@supplier_bp.route('/get_notifications')
@login_required
@supplier_required
def get_notifications():
    """AJAX endpoint for notifications"""
    # Mock implementation - replace with actual notification logic
    return jsonify({
        'new_notifications': 0,
        'notifications': []
    })

@supplier_bp.route('/reviews')
@login_required
@supplier_required
def reviews():
    """Supplier product reviews"""
    try:
        reviews = db.session.query(Review).join(Product)\
            .filter(Product.supplier_id == current_user.id)\
            .order_by(desc(Review.created_at)).all()
    except Exception as e:
        reviews = []
    
    return render_template('supplier/reviews.html', reviews=reviews)

@supplier_bp.route('/inventory')
@login_required
@supplier_required
def inventory():
    """Inventory management"""
    products = Product.query.filter_by(supplier_id=current_user.id)\
        .order_by(Product.stock_quantity.asc()).all()
    
    return render_template('supplier/inventory.html', products=products)

@supplier_bp.route('/orders/<int:order_id>')
@login_required
@supplier_required
def order_detail(order_id):
    """Order detail view"""
    order = Order.query.filter_by(id=order_id, supplier_id=current_user.id).first_or_404()
    return render_template('supplier/order_detail.html', order=order)
