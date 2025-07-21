# Admin Routes for MediPlant

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user, login_user
from functools import wraps
from app.database import db
from app.models import User, Product, Order, Category, SupplierProfile
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if current_user.is_authenticated and current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_admin():
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('admin/login.html')
            
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')
    
    return render_template('admin/login.html')

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get dashboard statistics
    total_users = User.query.count()
    total_suppliers = User.query.join(User.role).filter_by(name='supplier').count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_suppliers = SupplierProfile.query.filter_by(is_approved=False).count()
    
    stats = {
        'total_users': total_users,
        'total_suppliers': total_suppliers,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_suppliers': pending_suppliers
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users.html', users=users)

@admin_bp.route('/suppliers')
@login_required
@admin_required
def suppliers():
    """Manage suppliers"""
    page = request.args.get('page', 1, type=int)
    suppliers = SupplierProfile.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/suppliers.html', suppliers=suppliers)

@admin_bp.route('/suppliers/<int:supplier_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_supplier(supplier_id):
    """Approve supplier application"""
    supplier = SupplierProfile.query.get_or_404(supplier_id)
    supplier.is_approved = True
    supplier.approval_date = datetime.utcnow()
    
    db.session.commit()
    flash(f'Supplier {supplier.business_name} has been approved.', 'success')
    
    return redirect(url_for('admin.suppliers'))

@admin_bp.route('/products')
@login_required
@admin_required
def products():
    """Manage products"""
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/products.html', products=products)

@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    """Manage orders"""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytics dashboard"""
    # TODO: Implement analytics queries
    return render_template('admin/analytics.html')

@admin_bp.route('/messages')
@login_required
@admin_required
def messages():
    """Customer support messages"""
    # TODO: Implement message management
    return render_template('admin/messages.html')

@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API endpoint for dashboard statistics"""
    stats = {
        'users': User.query.count(),
        'products': Product.query.count(),
        'orders': Order.query.count(),
        'revenue': float(db.session.query(db.func.sum(Order.total_amount)).scalar() or 0)
    }
    return jsonify(stats)
