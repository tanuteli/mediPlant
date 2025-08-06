import os
import sqlite3
import uuid
import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = 'mediplant_secret_key_2025'

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def update_product_rating(product_id):
    """Update the average rating and total reviews for a product"""
    conn = get_db_connection()
    
    # Calculate average rating and total reviews
    rating_stats = conn.execute('''
        SELECT 
            AVG(CAST(rating AS REAL)) as avg_rating,
            COUNT(*) as total_reviews
        FROM reviews 
        WHERE product_id = ?
    ''', (product_id,)).fetchone()
    
    avg_rating = rating_stats['avg_rating'] or 0
    total_reviews = rating_stats['total_reviews'] or 0
    
    # Update product
    conn.execute('''
        UPDATE products 
        SET average_rating = ?, total_reviews = ?
        WHERE id = ?
    ''', (avg_rating, total_reviews, product_id))
    
    conn.commit()
    conn.close()

def calculate_order_total(subtotal):
    """Calculate final order total with taxes and shipping"""
    shipping = 0 if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_CHARGE
    gst = subtotal * GST_RATE
    total = subtotal + shipping + gst
    
    return {
        'subtotal': subtotal,
        'shipping': shipping,
        'gst': gst,
        'total': total,
        'free_shipping_threshold': FREE_SHIPPING_THRESHOLD
    }

# Currency configuration - Store prices in INR directly
# Shipping and tax configuration
FREE_SHIPPING_THRESHOLD = 2000  # INR
SHIPPING_CHARGE = 99  # INR
GST_RATE = 0.18  # 18% GST

# Indian States
INDIAN_STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat',
    'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh',
    'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh',
    'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh',
    'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir', 'Ladakh',
    'Lakshadweep', 'Puducherry'
]

# Add custom filter for Indian currency formatting
@app.template_filter('inr')
def format_inr(amount):
    """Format amount in Indian Rupees"""
    if amount is None:
        return "₹0.00"
    # Prices are already in INR
    return f"₹{float(amount):,.2f}"

@app.template_filter('inr_plain')
def format_inr_plain(amount):
    """Format amount in Indian Rupees without symbol"""
    if amount is None:
        return "0.00"
    # Prices are already in INR
    return f"{float(amount):,.2f}"

# Database configuration
DATABASE = 'mediplant.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.context_processor
def inject_categories():
    """Make categories available to all templates"""
    try:
        conn = get_db_connection()
        categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
        conn.close()
        return dict(categories=categories)
    except:
        return dict(categories=[])

def init_db():
    conn = get_db_connection()
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Categories table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Products table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            detailed_description TEXT,
            price REAL NOT NULL,
            category_id INTEGER,
            image_url TEXT,
            stock_quantity INTEGER DEFAULT 0,
            benefits TEXT,
            usage_instructions TEXT,
            warnings TEXT,
            is_active BOOLEAN DEFAULT 1,
            average_rating REAL DEFAULT 0,
            total_reviews INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # Cart table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Orders table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total_amount REAL,
            status TEXT DEFAULT 'pending',
            shipping_address TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            phone TEXT,
            payment_method TEXT DEFAULT 'cod',
            payment_status TEXT DEFAULT 'pending',
            tracking_number TEXT,
            estimated_delivery TIMESTAMP,
            delivered_at TIMESTAMP,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Order items table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Wishlist table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Reviews table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            review_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Authentication helper functions
def is_logged_in():
    return 'user_id' in session

def is_admin():
    if not is_logged_in():
        return False
    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return user and user['role'] == 'admin'

def login_required(f):
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def admin_required(f):
    def wrapper(*args, **kwargs):
        if not is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Routes
@app.route('/')
def index():
    conn = get_db_connection()
    
    # Get featured products based on highest ratings and recent activity
    featured_products = conn.execute('''
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        WHERE p.is_active = 1 
        ORDER BY p.average_rating DESC, p.total_reviews DESC, p.created_at DESC 
        LIMIT 6
    ''').fetchall()
    
    # Get categories
    categories = conn.execute('SELECT * FROM categories LIMIT 4').fetchall()
    
    conn.close()
    return render_template('index.html', featured_products=featured_products, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        phone = request.form.get('phone', '')
        
        if not username or not email or not password or not full_name:
            flash('All required fields must be filled.', 'danger')
            return render_template('register.html')
        
        conn = get_db_connection()
        
        # Check if user already exists
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?', 
            (username, email)
        ).fetchone()
        
        if existing_user:
            flash('Username or email already exists.', 'danger')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        conn.execute('''
            INSERT INTO users (username, email, password_hash, full_name, phone)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, phone))
        
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? OR email = ?', 
            (username, username)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    offset = (page - 1) * per_page
    
    category_id = request.args.get('category')
    search = request.args.get('search', '')
    
    conn = get_db_connection()
    
    # Build query
    query = '''
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        WHERE p.is_active = 1
    '''
    params = []
    
    if category_id:
        query += ' AND p.category_id = ?'
        params.append(category_id)
    
    if search:
        query += ' AND (p.name LIKE ? OR p.description LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    
    query += ' ORDER BY p.created_at DESC LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    products = conn.execute(query, params).fetchall()
    
    # Get categories for filter
    categories = conn.execute('SELECT * FROM categories').fetchall()
    
    conn.close()
    return render_template('products.html', products=products, categories=categories)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    
    product = conn.execute('''
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        WHERE p.id = ? AND p.is_active = 1
    ''', (product_id,)).fetchone()
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products'))
    
    # Get reviews
    reviews = conn.execute('''
        SELECT r.*, u.username, u.full_name
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.product_id = ?
        ORDER BY r.created_at DESC
    ''', (product_id,)).fetchall()
    
    # Get related products
    related_products = conn.execute('''
        SELECT * FROM products 
        WHERE category_id = ? AND id != ? AND is_active = 1 
        LIMIT 4
    ''', (product['category_id'], product_id)).fetchall()
    
    conn.close()
    return render_template('product_detail.html', product=product, reviews=reviews, related_products=related_products)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form['product_id']
    quantity = int(request.form.get('quantity', 1))
    
    conn = get_db_connection()
    
    # Check if item already in cart
    existing_item = conn.execute(
        'SELECT * FROM cart WHERE user_id = ? AND product_id = ?',
        (session['user_id'], product_id)
    ).fetchone()
    
    if existing_item:
        # Update quantity
        conn.execute(
            'UPDATE cart SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?',
            (quantity, session['user_id'], product_id)
        )
    else:
        # Add new item
        conn.execute(
            'INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
            (session['user_id'], product_id, quantity)
        )
    
    conn.commit()
    conn.close()
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        return jsonify({'success': True, 'message': 'Product added to cart!'})
    
    flash('Product added to cart!', 'success')
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    cart_id = request.form.get('cart_id')
    
    if not cart_id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Cart ID is required'})
        flash('Invalid request.', 'danger')
        return redirect(url_for('cart'))
    
    conn = get_db_connection()
    
    # Verify the cart item belongs to the current user
    cart_item = conn.execute('''
        SELECT * FROM cart WHERE id = ? AND user_id = ?
    ''', (cart_id, session['user_id'])).fetchone()
    
    if cart_item:
        conn.execute('DELETE FROM cart WHERE id = ?', (cart_id,))
        conn.commit()
        success = True
        message = 'Item removed from cart!'
    else:
        success = False
        message = 'Item not found or access denied'
    
    conn.close()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success, 'message': message})
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('cart'))

@app.route('/update_cart_quantity', methods=['POST'])
@login_required
def update_cart_quantity():
    cart_id = request.form.get('cart_id')
    new_quantity = request.form.get('quantity')
    
    if not cart_id or not new_quantity:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Cart ID and quantity are required'})
        flash('Invalid request.', 'danger')
        return redirect(url_for('cart'))
    
    try:
        new_quantity = int(new_quantity)
        if new_quantity < 1:
            raise ValueError("Quantity must be at least 1")
    except ValueError:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Invalid quantity'})
        flash('Invalid quantity.', 'danger')
        return redirect(url_for('cart'))
    
    conn = get_db_connection()
    
    # Verify the cart item belongs to the current user
    cart_item = conn.execute('''
        SELECT c.*, p.price FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.id = ? AND c.user_id = ?
    ''', (cart_id, session['user_id'])).fetchone()
    
    if cart_item:
        conn.execute('UPDATE cart SET quantity = ? WHERE id = ?', (new_quantity, cart_id))
        conn.commit()
        new_subtotal = float(cart_item['price']) * new_quantity
        success = True
        message = 'Quantity updated!'
    else:
        success = False
        message = 'Item not found or access denied'
        new_subtotal = 0
    
    conn.close()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': success, 
            'message': message,
            'new_subtotal': new_subtotal
        })
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    conn = get_db_connection()
    
    # Get cart items with product details and stock verification
    cart_items = conn.execute('''
        SELECT c.*, p.name, p.price, p.image_url, p.stock_quantity,
               (c.quantity * p.price) as subtotal
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ? AND p.is_active = 1
        ORDER BY c.created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    # Remove items that are out of stock
    valid_items = []
    for item in cart_items:
        if item['stock_quantity'] < item['quantity']:
            # Update cart quantity to available stock
            if item['stock_quantity'] > 0:
                conn.execute('''
                    UPDATE cart SET quantity = ? 
                    WHERE user_id = ? AND product_id = ?
                ''', (item['stock_quantity'], session['user_id'], item['product_id']))
                # Update the item for display
                item = dict(item)
                item['quantity'] = item['stock_quantity']
                item['subtotal'] = item['quantity'] * item['price']
                valid_items.append(item)
                flash(f'Updated {item["name"]} quantity to available stock ({item["stock_quantity"]})', 'warning')
            else:
                # Remove out of stock item
                conn.execute('''
                    DELETE FROM cart 
                    WHERE user_id = ? AND product_id = ?
                ''', (session['user_id'], item['product_id']))
                flash(f'{item["name"]} is out of stock and removed from cart', 'warning')
        else:
            valid_items.append(item)
    
    conn.commit()
    
    # Calculate totals
    if valid_items:
        subtotal = sum(item['subtotal'] for item in valid_items)
        order_totals = calculate_order_total(subtotal)
    else:
        subtotal = 0
        order_totals = {'subtotal': 0, 'gst': 0, 'shipping': 0, 'total': 0}
    
    conn.close()
    
    return render_template('cart.html', 
                         cart_items=valid_items,
                         **order_totals)

@app.route('/checkout')
@login_required
def checkout():
    conn = get_db_connection()
    
    # Get cart items with stock verification
    cart_items = conn.execute('''
        SELECT c.*, p.name, p.price, p.image_url, p.stock_quantity,
               (c.quantity * p.price) as subtotal
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ? AND p.is_active = 1
        ORDER BY c.created_at ASC
    ''', (session['user_id'],)).fetchall()
    
    if not cart_items:
        flash('Your cart is empty. Add some products to proceed with checkout.', 'warning')
        conn.close()
        return redirect(url_for('cart'))
    
    # Verify stock availability
    stock_issues = []
    valid_items = []
    
    for item in cart_items:
        if item['stock_quantity'] < item['quantity']:
            if item['stock_quantity'] > 0:
                stock_issues.append(f'{item["name"]} - only {item["stock_quantity"]} available')
                # Update cart to available quantity
                conn.execute('''
                    UPDATE cart SET quantity = ? 
                    WHERE user_id = ? AND product_id = ?
                ''', (item['stock_quantity'], session['user_id'], item['product_id']))
                # Update item for calculation
                item = dict(item)
                item['quantity'] = item['stock_quantity']
                item['subtotal'] = item['quantity'] * item['price']
                valid_items.append(item)
            else:
                stock_issues.append(f'{item["name"]} - out of stock')
                conn.execute('''
                    DELETE FROM cart 
                    WHERE user_id = ? AND product_id = ?
                ''', (session['user_id'], item['product_id']))
        else:
            valid_items.append(item)
    
    if stock_issues:
        for issue in stock_issues:
            flash(issue, 'warning')
        conn.commit()
        conn.close()
        return redirect(url_for('cart'))
    
    # Calculate order totals
    subtotal = sum(item['subtotal'] for item in valid_items)
    order_totals = calculate_order_total(subtotal)
    
    conn.close()
    
    return render_template('checkout.html', 
                         cart_items=valid_items,
                         **order_totals)

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    # Validate form data
    required_fields = ['shipping_address', 'city', 'state', 'postal_code', 'phone']
    for field in required_fields:
        if not request.form.get(field):
            flash(f'Please provide {field.replace("_", " ").title()}', 'danger')
            return redirect(url_for('checkout'))
    
    shipping_address = request.form['shipping_address']
    city = request.form['city']
    state = request.form['state']
    postal_code = request.form['postal_code']
    phone = request.form['phone']
    payment_method = request.form.get('payment_method', 'cod')
    
    conn = get_db_connection()
    
    try:
        # Get cart items with final stock check
        cart_items = conn.execute('''
            SELECT c.*, p.price, p.name, p.stock_quantity
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ? AND p.is_active = 1
        ''', (session['user_id'],)).fetchall()
        
        if not cart_items:
            flash('Your cart is empty.', 'warning')
            conn.close()
            return redirect(url_for('cart'))
        
        # Final stock validation
        for item in cart_items:
            if item['stock_quantity'] < item['quantity']:
                flash(f'Insufficient stock for {item["name"]}. Please update your cart.', 'danger')
                conn.close()
                return redirect(url_for('cart'))
        
        # Calculate final totals
        subtotal = sum(item['quantity'] * item['price'] for item in cart_items)
        order_totals = calculate_order_total(subtotal)
        final_total = order_totals['total']
        
        # Generate tracking number
        tracking_number = 'MP' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Create order
        cursor = conn.execute('''
            INSERT INTO orders (user_id, total_amount, shipping_address, city, state, 
                              postal_code, phone, payment_method, tracking_number, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], final_total, shipping_address, city, state, postal_code, 
              phone, payment_method, tracking_number, 'pending'))
        
        order_id = cursor.lastrowid
        
        # Add order items and update stock
        for item in cart_items:
            # Insert order item
            conn.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (order_id, item['product_id'], item['quantity'], item['price']))
            
            # Update product stock
            conn.execute('''
                UPDATE products SET stock_quantity = stock_quantity - ?
                WHERE id = ?
            ''', (item['quantity'], item['product_id']))
        
        # Clear user's cart
        conn.execute('DELETE FROM cart WHERE user_id = ?', (session['user_id'],))
        
        conn.commit()
        conn.close()
        
        flash(f'Order #{order_id} placed successfully! Your tracking number is {tracking_number}', 'success')
        return redirect(url_for('my_orders'))
        
    except Exception as e:
        conn.rollback()
        conn.close()
        flash('An error occurred while placing your order. Please try again.', 'danger')
        return redirect(url_for('checkout'))

@app.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    conn = get_db_connection()
    
    order = conn.execute('''
        SELECT o.*, u.full_name, u.email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.id = ? AND o.user_id = ?
    ''', (order_id, session['user_id'])).fetchone()
    
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('index'))
    
    order_items = conn.execute('''
        SELECT oi.*, p.name, p.image_url
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    
    conn.close()
    return render_template('order_confirmation.html', order=order, order_items=order_items)

@app.route('/my_orders')
@login_required
def my_orders():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    
    try:
        # Simple and reliable query to get user orders
        orders = conn.execute('''
            SELECT o.id, o.total_amount, o.status, o.shipping_address, o.city, o.state, 
                   o.postal_code, o.phone, o.payment_method, o.payment_status,
                   o.tracking_number, o.created_at
            FROM orders o
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC
            LIMIT ? OFFSET ?
        ''', (session['user_id'], per_page, offset)).fetchall()
        
        # Process orders and get additional data
        orders_list = []
        for order in orders:
            order_dict = dict(order)
            
            # Get order items for this order
            order_items = conn.execute('''
                SELECT oi.quantity, oi.price, p.name, p.image_url
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?
            ''', (order['id'],)).fetchall()
            
            # Calculate totals and product info
            total_items = sum(item['quantity'] for item in order_items)
            item_count = len(order_items)
            
            order_dict['total_items'] = total_items
            order_dict['item_count'] = item_count
            
            # Get product names (first 3)
            product_names = [item['name'] for item in order_items]
            order_dict['product_names_list'] = product_names[:3]
            order_dict['more_products'] = max(0, len(product_names) - 3)
            
            # Get first product image
            if order_items and order_items[0]['image_url']:
                order_dict['first_product_image'] = order_items[0]['image_url']
            else:
                order_dict['first_product_image'] = '/static/images/default-product.jpg'
            
            # Format created_at for better display
            if order_dict['created_at']:
                try:
                    from datetime import datetime
                    if isinstance(order_dict['created_at'], str):
                        created_date = datetime.strptime(order_dict['created_at'], '%Y-%m-%d %H:%M:%S')
                    else:
                        created_date = order_dict['created_at']
                    order_dict['created_at_formatted'] = created_date.strftime('%B %d, %Y at %I:%M %p')
                except Exception as date_error:
                    order_dict['created_at_formatted'] = str(order_dict['created_at'])
            else:
                order_dict['created_at_formatted'] = 'Unknown'
            
            orders_list.append(order_dict)
        
        # Get total count for pagination
        total_orders = conn.execute('''
            SELECT COUNT(*) as count FROM orders WHERE user_id = ?
        ''', (session['user_id'],)).fetchone()['count']
        
        # Get user statistics
        user_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_orders,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
                SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing_orders,
                SUM(CASE WHEN status = 'shipped' THEN 1 ELSE 0 END) as shipped_orders,
                SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_orders,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_orders,
                COALESCE(SUM(total_amount), 0) as total_spent
            FROM orders WHERE user_id = ?
        ''', (session['user_id'],)).fetchone()
        
        conn.close()
        
        # Calculate pagination
        total_pages = (total_orders + per_page - 1) // per_page if total_orders > 0 else 1
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('my_orders.html', 
                             orders=orders_list,
                             user_stats=user_stats,
                             page=page, 
                             total_pages=total_pages,
                             has_prev=has_prev, 
                             has_next=has_next,
                             total_orders=total_orders)
    
    except Exception as e:
        print(f"Error in my_orders: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.close()
        flash('Error loading orders. Please try again.', 'danger')
        return redirect(url_for('index'))


@app.route('/order_detail/<int:order_id>')
@login_required
def order_detail(order_id):
    conn = get_db_connection()
    
    # Get order details
    order = conn.execute('''
        SELECT o.*, u.full_name, u.email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.id = ? AND o.user_id = ?
    ''', (order_id, session['user_id'])).fetchone()
    
    if not order:
        flash('Order not found.', 'danger')
        conn.close()
        return redirect(url_for('my_orders'))
    
    # Get order items
    order_items = conn.execute('''
        SELECT oi.*, p.name, p.image_url, p.description
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    
    conn.close()
    return render_template('order_detail.html', order=order, order_items=order_items)

@app.route('/add_review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    rating = int(request.form['rating'])
    review_text = request.form.get('review_text', '')
    
    if not (1 <= rating <= 5):
        flash('Invalid rating. Please select a rating between 1 and 5.', 'danger')
        return redirect(url_for('product_detail', product_id=product_id))
    
    conn = get_db_connection()
    
    # Check if user has already reviewed this product
    existing_review = conn.execute('''
        SELECT id FROM reviews WHERE user_id = ? AND product_id = ?
    ''', (session['user_id'], product_id)).fetchone()
    
    if existing_review:
        # Update existing review
        conn.execute('''
            UPDATE reviews SET rating = ?, review_text = ?
            WHERE user_id = ? AND product_id = ?
        ''', (rating, review_text, session['user_id'], product_id))
        flash('Your review has been updated!', 'success')
    else:
        # Add new review
        conn.execute('''
            INSERT INTO reviews (user_id, product_id, rating, review_text)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], product_id, rating, review_text))
        flash('Thank you for your review!', 'success')
    
    conn.commit()
    conn.close()
    
    # Update product rating
    update_product_rating(product_id)
    
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    conn = get_db_connection()
    
    # Get review to check ownership and get product_id
    review = conn.execute('''
        SELECT * FROM reviews WHERE id = ? AND user_id = ?
    ''', (review_id, session['user_id'])).fetchone()
    
    if not review:
        flash('Review not found or you do not have permission to delete it.', 'danger')
    else:
        product_id = review['product_id']
        conn.execute('DELETE FROM reviews WHERE id = ?', (review_id,))
        conn.commit()
        flash('Review deleted successfully.', 'success')
        
        # Update product rating
        update_product_rating(product_id)
    
    conn.close()
    return redirect(request.referrer or url_for('index'))

# Wishlist routes
@app.route('/wishlist')
@login_required
def wishlist():
    conn = get_db_connection()
    
    wishlist_items = conn.execute('''
        SELECT w.*, p.name, p.price, p.image_url, p.stock_quantity, c.name as category_name
        FROM wishlist w
        JOIN products p ON w.product_id = p.id
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE w.user_id = ? AND p.is_active = 1
        ORDER BY w.created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    return render_template('wishlist.html', wishlist_items=wishlist_items)

@app.route('/add_to_wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    product_id = request.form['product_id']
    
    conn = get_db_connection()
    
    # Check if already in wishlist
    existing = conn.execute('''
        SELECT id FROM wishlist WHERE user_id = ? AND product_id = ?
    ''', (session['user_id'], product_id)).fetchone()
    
    if existing:
        message = 'Product is already in your wishlist.'
        success = False
    else:
        conn.execute('''
            INSERT INTO wishlist (user_id, product_id)
            VALUES (?, ?)
        ''', (session['user_id'], product_id))
        conn.commit()
        message = 'Product added to wishlist!'
        success = True
    
    conn.close()
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success, 'message': message})
    
    flash(message, 'success' if success else 'info')
    return redirect(request.referrer or url_for('products'))

@app.route('/remove_from_wishlist/<int:wishlist_id>', methods=['POST'])
@login_required
def remove_from_wishlist(wishlist_id):
    conn = get_db_connection()
    
    # Verify ownership
    wishlist_item = conn.execute('''
        SELECT * FROM wishlist WHERE id = ? AND user_id = ?
    ''', (wishlist_id, session['user_id'])).fetchone()
    
    if wishlist_item:
        conn.execute('DELETE FROM wishlist WHERE id = ?', (wishlist_id,))
        conn.commit()
        flash('Product removed from wishlist.', 'success')
    
    conn.close()
    return redirect(url_for('wishlist'))

@app.route('/remove_from_wishlist', methods=['POST'])
@login_required
def remove_from_wishlist_ajax():
    wishlist_id = request.form.get('wishlist_id')
    
    if not wishlist_id:
        return jsonify({'success': False, 'message': 'Missing wishlist ID'})
    
    conn = get_db_connection()
    
    # Verify ownership
    wishlist_item = conn.execute('''
        SELECT * FROM wishlist WHERE id = ? AND user_id = ?
    ''', (wishlist_id, session['user_id'])).fetchone()
    
    if wishlist_item:
        conn.execute('DELETE FROM wishlist WHERE id = ?', (wishlist_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Product removed from wishlist'})
    else:
        conn.close()
        return jsonify({'success': False, 'message': 'Item not found or access denied'})

@app.route('/move_to_cart/<int:wishlist_id>', methods=['POST'])
@login_required
def move_to_cart(wishlist_id):
    conn = get_db_connection()
    
    # Get wishlist item
    wishlist_item = conn.execute('''
        SELECT * FROM wishlist WHERE id = ? AND user_id = ?
    ''', (wishlist_id, session['user_id'])).fetchone()
    
    if wishlist_item:
        product_id = wishlist_item['product_id']
        
        # Check if already in cart
        existing_cart = conn.execute('''
            SELECT * FROM cart WHERE user_id = ? AND product_id = ?
        ''', (session['user_id'], product_id)).fetchone()
        
        if existing_cart:
            # Update quantity
            conn.execute('''
                UPDATE cart SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?
            ''', (session['user_id'], product_id))
        else:
            # Add to cart
            conn.execute('''
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (?, ?, 1)
            ''', (session['user_id'], product_id))
        
        # Remove from wishlist
        conn.execute('DELETE FROM wishlist WHERE id = ?', (wishlist_id,))
        conn.commit()
        flash('Product moved to cart!', 'success')
    
    conn.close()
    return redirect(url_for('wishlist'))

@app.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    conn = get_db_connection()
    
    # Get order to check ownership and status
    order = conn.execute('''
        SELECT * FROM orders WHERE id = ? AND user_id = ?
    ''', (order_id, session['user_id'])).fetchone()
    
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'})
    
    if order['status'] != 'pending':
        return jsonify({'success': False, 'message': 'Order cannot be cancelled'})
    
    # Get reason from JSON or form data, default to customer cancellation
    reason = 'Cancelled by customer'
    try:
        if request.is_json and request.json:
            reason = request.json.get('reason', reason)
        elif request.form:
            reason = request.form.get('reason', reason)
    except:
        pass
    
    # Update order status
    conn.execute('''
        UPDATE orders SET status = 'cancelled', notes = ?
        WHERE id = ?
    ''', (reason, order_id))
    
    # Restore stock quantities
    order_items = conn.execute('''
        SELECT product_id, quantity FROM order_items WHERE order_id = ?
    ''', (order_id,)).fetchall()
    
    for item in order_items:
        conn.execute('''
            UPDATE products SET stock_quantity = stock_quantity + ?
            WHERE id = ?
        ''', (item['quantity'], item['product_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Order cancelled successfully'})

@app.route('/download_invoice/<int:order_id>')
@login_required
def download_invoice(order_id):
    conn = get_db_connection()
    
    # Get order details
    order = conn.execute('''
        SELECT o.*, u.full_name, u.email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.id = ? AND o.user_id = ?
    ''', (order_id, session['user_id'])).fetchone()
    
    if not order:
        flash('Order not found.', 'danger')
        conn.close()
        return redirect(url_for('my_orders'))
    
    # Get order items
    order_items = conn.execute('''
        SELECT oi.*, p.name, p.description
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    
    conn.close()
    
    # For now, render an invoice template
    # In production, you might want to generate a PDF
    return render_template('invoice.html', order=order, order_items=order_items)

# Admin Routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    
    # Get stats
    total_users = conn.execute('SELECT COUNT(*) as count FROM users WHERE role = "user"').fetchone()['count']
    total_products = conn.execute('SELECT COUNT(*) as count FROM products WHERE is_active = 1').fetchone()['count']
    total_orders = conn.execute('SELECT COUNT(*) as count FROM orders').fetchone()['count']
    total_revenue = conn.execute('SELECT COALESCE(SUM(total_amount), 0) as revenue FROM orders').fetchone()['revenue']
    
    # Recent orders
    recent_orders = conn.execute('''
        SELECT o.*, u.full_name, u.email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    return render_template('admin/dashboard.html', 
                         total_users=total_users, 
                         total_products=total_products,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders)

@app.route('/admin/products')
@admin_required
def admin_products():
    conn = get_db_connection()
    
    products = conn.execute('''
        SELECT p.*, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.is_active = 1
        ORDER BY p.created_at DESC
    ''').fetchall()
    
    conn.close()
    return render_template('admin/products.html', products=products)

@app.route('/admin/add_product', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        detailed_description = request.form.get('detailed_description', '')
        price = float(request.form['price'])
        category_id = request.form['category_id']
        stock_quantity = int(request.form.get('stock_quantity', 0))
        benefits = request.form.get('benefits', '')
        usage_instructions = request.form.get('usage_instructions', '')
        warnings = request.form.get('warnings', '')
        
        # Handle image upload or URL
        image_url = request.form.get('image_url', '')
        if 'main_image' in request.files and request.files['main_image'].filename:
            file = request.files['main_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create unique filename
                import uuid
                ext = filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = f'/static/uploads/{filename}'
        elif not image_url:
            image_url = '/static/images/default-product.jpg'
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO products (name, description, detailed_description, price, category_id, 
                                image_url, stock_quantity, benefits, usage_instructions, warnings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, detailed_description, price, category_id, image_url, 
              stock_quantity, benefits, usage_instructions, warnings))
        
        conn.commit()
        conn.close()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    
    return render_template('admin/product_form.html', categories=categories)

@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        full_name = request.form['full_name']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        postal_code = request.form.get('postal_code', '')
        role = request.form.get('role', 'user')
        is_active = 1 if request.form.get('is_active') else 0
        
        # Check if username/email exists for other users
        existing_user = conn.execute('''
            SELECT id FROM users 
            WHERE (username = ? OR email = ?) AND id != ?
        ''', (username, email, user_id)).fetchone()
        
        if existing_user:
            flash('Username or email already exists for another user.', 'danger')
        else:
            conn.execute('''
                UPDATE users SET 
                    username = ?, email = ?, full_name = ?, phone = ?,
                    address = ?, city = ?, state = ?, postal_code = ?,
                    role = ?, is_active = ?
                WHERE id = ?
            ''', (username, email, full_name, phone, address, city, state, 
                  postal_code, role, is_active, user_id))
            
            conn.commit()
            flash('User updated successfully!', 'success')
            conn.close()
            return redirect(url_for('admin_users'))
    
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/edit_user.html', user=user, states=INDIAN_STATES)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    # Prevent admin from deleting themselves
    if user_id == session['user_id']:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_users'))
    
    conn = get_db_connection()
    
    # Check if user has orders
    orders_count = conn.execute('SELECT COUNT(*) as count FROM orders WHERE user_id = ?', (user_id,)).fetchone()['count']
    
    if orders_count > 0:
        # Deactivate instead of delete
        conn.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
        flash('User account deactivated (has order history).', 'warning')
    else:
        # Safe to delete
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        flash('User deleted successfully!', 'success')
    
    conn.commit()
    conn.close()
    return redirect(url_for('admin_users'))

@app.route('/admin/add_user', methods=['GET', 'POST'])
@admin_required
def admin_add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        postal_code = request.form.get('postal_code', '')
        role = request.form.get('role', 'user')
        
        if not username or not email or not password or not full_name:
            flash('Required fields must be filled.', 'danger')
            return render_template('admin/add_user.html', states=INDIAN_STATES)
        
        conn = get_db_connection()
        
        # Check if user already exists
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?', 
            (username, email)
        ).fetchone()
        
        if existing_user:
            flash('Username or email already exists.', 'danger')
            conn.close()
            return render_template('admin/add_user.html', states=INDIAN_STATES)
        
        # Create new user
        password_hash = generate_password_hash(password)
        conn.execute('''
            INSERT INTO users (username, email, password_hash, full_name, phone,
                             address, city, state, postal_code, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, phone,
              address, city, state, postal_code, role))
        
        conn.commit()
        conn.close()
        
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/add_user.html', states=INDIAN_STATES)

@app.route('/admin/orders')
@admin_required
def admin_orders():
    # Get filter parameters
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    
    # Build query with filters
    base_query = '''
        SELECT o.*, u.full_name, u.email, u.phone,
               COUNT(oi.id) as item_count,
               SUM(oi.quantity) as total_items
        FROM orders o
        JOIN users u ON o.user_id = u.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
    '''
    
    conditions = []
    params = []
    
    if status_filter:
        conditions.append('o.status = ?')
        params.append(status_filter)
    
    if search_query:
        conditions.append('(u.full_name LIKE ? OR u.email LIKE ? OR o.tracking_number LIKE ?)')
        search_param = f'%{search_query}%'
        params.extend([search_param, search_param, search_param])
    
    where_clause = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
    
    # Get orders with pagination
    orders_query = base_query + where_clause + '''
        GROUP BY o.id
        ORDER BY o.created_at DESC
        LIMIT ? OFFSET ?
    '''
    params.extend([per_page, offset])
    
    orders = conn.execute(orders_query, params).fetchall()
    
    # Get total count for pagination
    count_query = '''
        SELECT COUNT(DISTINCT o.id) as count
        FROM orders o
        JOIN users u ON o.user_id = u.id
    ''' + where_clause
    
    total_orders = conn.execute(count_query, params[:-2]).fetchone()['count']
    
    # Get order statistics
    stats = conn.execute('''
        SELECT 
            COUNT(*) as total_orders,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
            SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing_orders,
            SUM(CASE WHEN status = 'shipped' THEN 1 ELSE 0 END) as shipped_orders,
            SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_orders,
            SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_orders,
            SUM(total_amount) as total_revenue
        FROM orders
    ''').fetchone()
    
    conn.close()
    
    # Calculate pagination
    total_pages = (total_orders + per_page - 1) // per_page if total_orders > 0 else 1
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('admin/orders.html', 
                         orders=orders,
                         stats=stats,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         status_filter=status_filter,
                         search_query=search_query,
                         total_orders=total_orders)

@app.route('/admin/order/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    conn = get_db_connection()
    
    order = conn.execute('''
        SELECT o.*, u.full_name, u.email, u.phone
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.id = ?
    ''', (order_id,)).fetchone()
    
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('admin_orders'))
    
    order_items = conn.execute('''
        SELECT oi.*, p.name, p.image_url
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    
    conn.close()
    return render_template('admin/order_detail.html', order=order, order_items=order_items)

@app.route('/admin/update_order_status', methods=['POST'])
@admin_required
def update_order_status():
    order_id = request.form['order_id']
    new_status = request.form['status']
    
    try:
        conn = get_db_connection()
        conn.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
        conn.commit()
        conn.close()
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'new_status': new_status,
                'message': f'Order status updated to {new_status.title()}!'
            })
        else:
            flash(f'Order status updated to {new_status.title()}!', 'success')
            return redirect(url_for('admin_order_detail', order_id=order_id))
    
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        else:
            flash('Error updating order status. Please try again.', 'error')
            return redirect(url_for('admin_order_detail', order_id=order_id))

@app.route('/admin/categories')
@admin_required
def admin_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/add_category', methods=['GET', 'POST'])
@admin_required
def admin_add_category():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image_url = request.form.get('image_url', '')
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO categories (name, description, image_url)
            VALUES (?, ?, ?)
        ''', (name, description, image_url))
        
        conn.commit()
        conn.close()
        
        flash('Category added successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/add_category.html')

@app.route('/admin/edit_category/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_category(category_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image_url = request.form.get('image_url', '')
        
        conn.execute('''
            UPDATE categories SET name = ?, description = ?, image_url = ?
            WHERE id = ?
        ''', (name, description, image_url, category_id))
        
        conn.commit()
        conn.close()
        
        flash('Category updated successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    category = conn.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()
    conn.close()
    
    if not category:
        flash('Category not found.', 'danger')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/edit_category.html', category=category)

@app.route('/admin/delete_category/<int:category_id>', methods=['POST'])
@admin_required
def admin_delete_category(category_id):
    conn = get_db_connection()
    
    # Check if category has products
    products_count = conn.execute('SELECT COUNT(*) as count FROM products WHERE category_id = ?', (category_id,)).fetchone()['count']
    
    if products_count > 0:
        flash(f'Cannot delete category. It has {products_count} products associated with it.', 'danger')
    else:
        conn.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        conn.commit()
        flash('Category deleted successfully!', 'success')
    
    conn.close()
    return redirect(url_for('admin_categories'))

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        detailed_description = request.form.get('detailed_description', '')
        price = float(request.form['price'])
        category_id = request.form['category_id']
        stock_quantity = int(request.form.get('stock_quantity', 0))
        benefits = request.form.get('benefits', '')
        usage_instructions = request.form.get('usage_instructions', '')
        warnings = request.form.get('warnings', '')
        is_active = 1 if request.form.get('is_active') else 0
        
        # Get current product to preserve existing image if no new one uploaded
        current_product = conn.execute('SELECT image_url FROM products WHERE id = ?', (product_id,)).fetchone()
        image_url = current_product['image_url'] if current_product else '/static/images/default-product.jpg'
        
        # Handle image upload or URL
        new_image_url = request.form.get('image_url', '')
        if 'main_image' in request.files and request.files['main_image'].filename:
            file = request.files['main_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create unique filename
                import uuid
                ext = filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = f'/static/uploads/{filename}'
        elif new_image_url:
            image_url = new_image_url
        
        conn.execute('''
            UPDATE products SET name = ?, description = ?, detailed_description = ?, 
                              price = ?, category_id = ?, image_url = ?, stock_quantity = ?,
                              benefits = ?, usage_instructions = ?, warnings = ?, is_active = ?
            WHERE id = ?
        ''', (name, description, detailed_description, price, category_id, image_url, 
              stock_quantity, benefits, usage_instructions, warnings, is_active, product_id))
        
        conn.commit()
        conn.close()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/edit_product.html', product=product, categories=categories)

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    conn = get_db_connection()
    conn.execute('UPDATE products SET is_active = 0 WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    
    flash('Product deactivated successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/products/<int:product_id>/delete', methods=['DELETE'])
@admin_required
def admin_delete_product_api(product_id):
    try:
        conn = get_db_connection()
        conn.execute('UPDATE products SET is_active = 0 WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Product deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    conn = get_db_connection()
    
    # Sales analytics
    monthly_sales = conn.execute('''
        SELECT 
            strftime('%Y-%m', created_at) as month,
            COUNT(*) as order_count,
            SUM(total_amount) as revenue
        FROM orders 
        WHERE status != 'cancelled'
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month DESC
        LIMIT 12
    ''').fetchall()
    
    # Top selling products
    top_products = conn.execute('''
        SELECT 
            p.name,
            SUM(oi.quantity) as total_sold,
            SUM(oi.quantity * oi.price) as revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status != 'cancelled'
        GROUP BY p.id, p.name
        ORDER BY total_sold DESC
        LIMIT 10
    ''').fetchall()
    
    # Order status distribution
    order_stats = conn.execute('''
        SELECT 
            status,
            COUNT(*) as count
        FROM orders
        GROUP BY status
    ''').fetchall()
    
    # User registration trends
    user_stats = conn.execute('''
        SELECT 
            strftime('%Y-%m', created_at) as month,
            COUNT(*) as new_users
        FROM users
        WHERE role = 'user'
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month DESC
        LIMIT 12
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin/analytics.html', 
                         monthly_sales=monthly_sales,
                         top_products=top_products,
                         order_stats=order_stats,
                         user_stats=user_stats)

@app.route('/admin/settings')
@admin_required
def admin_settings():
    return render_template('admin/settings.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
