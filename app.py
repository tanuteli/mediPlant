import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = 'mediplant_secret_key_2025'

# Currency conversion rate (1 USD = 75 INR approximately)
USD_TO_INR_RATE = 75

# Add custom filter for Indian currency formatting
@app.template_filter('inr')
def format_inr(amount):
    """Format amount in Indian Rupees"""
    if amount is None:
        return "₹0.00"
    # Convert USD to INR
    inr_amount = float(amount) * USD_TO_INR_RATE
    return f"₹{inr_amount:,.2f}"

@app.template_filter('inr_plain')
def format_inr_plain(amount):
    """Format amount in Indian Rupees without symbol"""
    if amount is None:
        return "0.00"
    # Convert USD to INR
    inr_amount = float(amount) * USD_TO_INR_RATE
    return f"{inr_amount:,.2f}"

# Database configuration
DATABASE = 'mediplant.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

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
    
    # Get featured products (latest 6 products)
    featured_products = conn.execute('''
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        WHERE p.is_active = 1 
        ORDER BY p.created_at DESC 
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
    
    flash('Product added to cart!', 'success')
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/cart')
@login_required
def cart():
    conn = get_db_connection()
    
    cart_items = conn.execute('''
        SELECT c.*, p.name, p.price, p.image_url, (c.quantity * p.price) as subtotal
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    total = sum(item['subtotal'] for item in cart_items)
    
    conn.close()
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/checkout')
@login_required
def checkout():
    conn = get_db_connection()
    
    cart_items = conn.execute('''
        SELECT c.*, p.name, p.price, p.image_url, (c.quantity * p.price) as subtotal
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart'))
    
    total = sum(item['subtotal'] for item in cart_items)
    
    conn.close()
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    shipping_address = request.form['shipping_address']
    
    conn = get_db_connection()
    
    # Get cart items
    cart_items = conn.execute('''
        SELECT c.*, p.price
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart'))
    
    # Calculate total
    total = sum(item['quantity'] * item['price'] for item in cart_items)
    
    # Create order
    cursor = conn.execute('''
        INSERT INTO orders (user_id, total_amount, shipping_address)
        VALUES (?, ?, ?)
    ''', (session['user_id'], total, shipping_address))
    
    order_id = cursor.lastrowid
    
    # Add order items
    for item in cart_items:
        conn.execute('''
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        ''', (order_id, item['product_id'], item['quantity'], item['price']))
    
    # Clear cart
    conn.execute('DELETE FROM cart WHERE user_id = ?', (session['user_id'],))
    
    conn.commit()
    conn.close()
    
    flash('Order placed successfully!', 'success')
    return redirect(url_for('order_confirmation', order_id=order_id))

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
        image_url = request.form.get('image_url', '/static/images/default-product.jpg')
        stock_quantity = int(request.form.get('stock_quantity', 0))
        benefits = request.form.get('benefits', '')
        usage_instructions = request.form.get('usage_instructions', '')
        warnings = request.form.get('warnings', '')
        
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
    
    return render_template('admin/add_product.html', categories=categories)

@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)

@app.route('/admin/orders')
@admin_required
def admin_orders():
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT o.*, u.full_name, u.email, u.phone
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('admin/orders.html', orders=orders)

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
        image_url = request.form.get('image_url', '/static/images/default-product.jpg')
        stock_quantity = int(request.form.get('stock_quantity', 0))
        benefits = request.form.get('benefits', '')
        usage_instructions = request.form.get('usage_instructions', '')
        warnings = request.form.get('warnings', '')
        is_active = 1 if request.form.get('is_active') else 0
        
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
