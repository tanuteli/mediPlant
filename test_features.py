#!/usr/bin/env python3
"""
Test vital features of MediPlant webapp
"""

import sqlite3
import requests
import json

def test_database_integrity():
    """Test database relationships and data integrity"""
    print("🔍 Testing Database Integrity...")
    
    conn = sqlite3.connect('mediplant.db')
    conn.row_factory = sqlite3.Row
    
    # Test 1: All products have valid categories
    invalid_categories = conn.execute('''
        SELECT COUNT(*) as count 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        WHERE p.category_id IS NOT NULL AND c.id IS NULL
    ''').fetchone()['count']
    
    if invalid_categories == 0:
        print("✅ All products have valid categories")
    else:
        print(f"❌ {invalid_categories} products with invalid categories")
    
    # Test 2: No orphaned cart items
    orphaned_cart = conn.execute('''
        SELECT COUNT(*) as count 
        FROM cart c 
        LEFT JOIN users u ON c.user_id = u.id 
        LEFT JOIN products p ON c.product_id = p.id 
        WHERE u.id IS NULL OR p.id IS NULL
    ''').fetchone()['count']
    
    if orphaned_cart == 0:
        print("✅ No orphaned cart items")
    else:
        print(f"❌ {orphaned_cart} orphaned cart items")
    
    # Test 3: No orphaned wishlist items  
    orphaned_wishlist = conn.execute('''
        SELECT COUNT(*) as count 
        FROM wishlist w 
        LEFT JOIN users u ON w.user_id = u.id 
        LEFT JOIN products p ON w.product_id = p.id 
        WHERE u.id IS NULL OR p.id IS NULL
    ''').fetchone()['count']
    
    if orphaned_wishlist == 0:
        print("✅ No orphaned wishlist items")
    else:
        print(f"❌ {orphaned_wishlist} orphaned wishlist items")
    
    # Test 4: All users have required fields
    invalid_users = conn.execute('''
        SELECT COUNT(*) as count 
        FROM users 
        WHERE username IS NULL OR username = '' 
           OR email IS NULL OR email = ''
           OR full_name IS NULL OR full_name = ''
    ''').fetchone()['count']
    
    if invalid_users == 0:
        print("✅ All users have required fields")
    else:
        print(f"❌ {invalid_users} users missing required fields")
    
    # Test 5: Product ratings are valid
    invalid_ratings = conn.execute('''
        SELECT COUNT(*) as count 
        FROM products 
        WHERE average_rating < 0 OR average_rating > 5
    ''').fetchone()['count']
    
    if invalid_ratings == 0:
        print("✅ All product ratings are valid (0-5)")
    else:
        print(f"❌ {invalid_ratings} products with invalid ratings")
    
    conn.close()

def test_route_accessibility():
    """Test that all vital routes are accessible"""
    print("\n🌐 Testing Route Accessibility...")
    
    base_url = "http://127.0.0.1:5000"
    
    # Test public routes
    public_routes = [
        "/",
        "/products", 
        "/login",
        "/register"
    ]
    
    for route in public_routes:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {route} - Accessible")
            else:
                print(f"❌ {route} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {route} - Error: {str(e)}")

def test_cart_functionality():
    """Test cart operations"""
    print("\n🛒 Testing Cart Functionality...")
    
    conn = sqlite3.connect('mediplant.db')
    
    # Check if we have test users and products
    users = conn.execute("SELECT id FROM users WHERE role = 'user' LIMIT 1").fetchone()
    products = conn.execute("SELECT id FROM products WHERE is_active = 1 LIMIT 1").fetchone()
    
    if not users or not products:
        print("❌ Need test users and products for cart testing")
        conn.close()
        return
    
    user_id = users[0]
    product_id = products[0]
    
    # Clear existing cart for test user
    conn.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    
    # Add item to cart
    conn.execute("""
        INSERT INTO cart (user_id, product_id, quantity) 
        VALUES (?, ?, ?)
    """, (user_id, product_id, 2))
    
    # Check if item was added
    cart_item = conn.execute("""
        SELECT * FROM cart WHERE user_id = ? AND product_id = ?
    """, (user_id, product_id)).fetchone()
    
    if cart_item:
        print("✅ Cart - Add item works")
        
        # Test cart view query
        cart_items = conn.execute('''
            SELECT c.*, p.name, p.price, p.image_url, (c.quantity * p.price) as subtotal
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
        ''', (user_id,)).fetchall()
        
        if cart_items:
            print("✅ Cart - View query works")
        else:
            print("❌ Cart - View query failed")
    else:
        print("❌ Cart - Add item failed")
    
    conn.commit()
    conn.close()

def test_order_functionality():
    """Test order operations"""
    print("\n📦 Testing Order Functionality...")
    
    conn = sqlite3.connect('mediplant.db')
    
    # Check if we have test data
    users = conn.execute("SELECT id FROM users WHERE role = 'user' LIMIT 1").fetchone()
    
    if not users:
        print("❌ Need test users for order testing")
        conn.close()
        return
    
    user_id = users[0]
    
    # Create a test order
    cursor = conn.execute('''
        INSERT INTO orders (user_id, total_amount, shipping_address, status)
        VALUES (?, ?, ?, ?)
    ''', (user_id, 1500.00, "Test Address", "pending"))
    
    order_id = cursor.lastrowid
    
    if order_id:
        print("✅ Orders - Create order works")
        
        # Test order view query
        order = conn.execute('''
            SELECT o.*, u.full_name, u.email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.id = ?
        ''', (order_id,)).fetchone()
        
        if order:
            print("✅ Orders - View query works")
        else:
            print("❌ Orders - View query failed")
    else:
        print("❌ Orders - Create order failed")
    
    conn.commit()
    conn.close()

def test_admin_functionality():
    """Test admin operations"""
    print("\n👑 Testing Admin Functionality...")
    
    conn = sqlite3.connect('mediplant.db')
    
    # Check if we have admin users
    admin_users = conn.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1").fetchone()
    
    if not admin_users:
        print("❌ No admin users found")
        conn.close()
        return
    
    print("✅ Admin users exist")
    
    # Test admin queries
    try:
        # Dashboard stats
        total_users = conn.execute('SELECT COUNT(*) as count FROM users WHERE role = "user"').fetchone()[0]
        total_products = conn.execute('SELECT COUNT(*) as count FROM products WHERE is_active = 1').fetchone()[0]
        total_orders = conn.execute('SELECT COUNT(*) as count FROM orders').fetchone()[0]
        
        print(f"✅ Admin Dashboard - {total_users} users, {total_products} products, {total_orders} orders")
        
        # Products query
        products = conn.execute('''
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LIMIT 1
        ''').fetchone()
        
        if products:
            print("✅ Admin Products - Query works")
        else:
            print("❌ Admin Products - Query failed")
            
    except Exception as e:
        print(f"❌ Admin queries failed: {str(e)}")
    
    conn.close()

def test_wishlist_functionality():
    """Test wishlist operations"""
    print("\n💝 Testing Wishlist Functionality...")
    
    conn = sqlite3.connect('mediplant.db')
    
    # Check if we have test data
    users = conn.execute("SELECT id FROM users WHERE role = 'user' LIMIT 1").fetchone()
    products = conn.execute("SELECT id FROM products WHERE is_active = 1 LIMIT 1").fetchone()
    
    if not users or not products:
        print("❌ Need test users and products for wishlist testing")
        conn.close()
        return
    
    user_id = users[0]
    product_id = products[0]
    
    # Clear existing wishlist for test user
    conn.execute("DELETE FROM wishlist WHERE user_id = ?", (user_id,))
    
    # Add item to wishlist
    conn.execute("""
        INSERT INTO wishlist (user_id, product_id) 
        VALUES (?, ?)
    """, (user_id, product_id))
    
    # Check if item was added
    wishlist_item = conn.execute("""
        SELECT * FROM wishlist WHERE user_id = ? AND product_id = ?
    """, (user_id, product_id)).fetchone()
    
    if wishlist_item:
        print("✅ Wishlist - Add item works")
        
        # Test wishlist view query
        wishlist_items = conn.execute('''
            SELECT w.*, p.name, p.price, p.image_url, c.name as category_name
            FROM wishlist w
            JOIN products p ON w.product_id = p.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE w.user_id = ?
        ''', (user_id,)).fetchall()
        
        if wishlist_items:
            print("✅ Wishlist - View query works")
        else:
            print("❌ Wishlist - View query failed")
    else:
        print("❌ Wishlist - Add item failed")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("🧪 MediPlant Vital Features Test")
    print("=" * 50)
    
    test_database_integrity()
    test_route_accessibility()
    test_cart_functionality()
    test_order_functionality()
    test_admin_functionality()
    test_wishlist_functionality()
    
    print("\n" + "=" * 50)
    print("✨ Testing Complete!")
