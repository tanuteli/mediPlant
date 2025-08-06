#!/usr/bin/env python3
"""
Comprehensive analysis script for MediPlant webapp
- Scans database for duplicates and issues
- Analyzes code for redundancies
- Verifies vital features
"""

import sqlite3
import os
import re
from datetime import datetime

def analyze_database():
    """Analyze database for duplicates and issues"""
    print("=== DATABASE ANALYSIS ===")
    
    if not os.path.exists('mediplant.db'):
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect('mediplant.db')
    conn.row_factory = sqlite3.Row
    
    # Check all tables
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"📊 Found {len(tables)} tables:")
    
    for table in tables:
        table_name = table['name']
        count = conn.execute(f"SELECT COUNT(*) as count FROM {table_name}").fetchone()['count']
        print(f"  - {table_name}: {count} records")
    
    # Check for duplicate users
    print("\n🔍 Checking for duplicates...")
    
    # Duplicate usernames
    dup_users = conn.execute("""
        SELECT username, COUNT(*) as count 
        FROM users 
        GROUP BY username 
        HAVING count > 1
    """).fetchall()
    
    if dup_users:
        print("❌ Duplicate usernames found:")
        for user in dup_users:
            print(f"  - {user['username']}: {user['count']} occurrences")
    else:
        print("✅ No duplicate usernames")
    
    # Duplicate emails
    dup_emails = conn.execute("""
        SELECT email, COUNT(*) as count 
        FROM users 
        GROUP BY email 
        HAVING count > 1
    """).fetchall()
    
    if dup_emails:
        print("❌ Duplicate emails found:")
        for email in dup_emails:
            print(f"  - {email['email']}: {email['count']} occurrences")
    else:
        print("✅ No duplicate emails")
    
    # Orphaned cart items
    orphaned_cart = conn.execute("""
        SELECT COUNT(*) as count 
        FROM cart c 
        LEFT JOIN users u ON c.user_id = u.id 
        LEFT JOIN products p ON c.product_id = p.id 
        WHERE u.id IS NULL OR p.id IS NULL
    """).fetchone()['count']
    
    if orphaned_cart > 0:
        print(f"❌ {orphaned_cart} orphaned cart items found")
    else:
        print("✅ No orphaned cart items")
    
    # Orphaned wishlist items
    orphaned_wishlist = conn.execute("""
        SELECT COUNT(*) as count 
        FROM wishlist w 
        LEFT JOIN users u ON w.user_id = u.id 
        LEFT JOIN products p ON w.product_id = p.id 
        WHERE u.id IS NULL OR p.id IS NULL
    """).fetchone()['count']
    
    if orphaned_wishlist > 0:
        print(f"❌ {orphaned_wishlist} orphaned wishlist items found")
    else:
        print("✅ No orphaned wishlist items")
    
    # Check for products without categories
    products_no_cat = conn.execute("""
        SELECT COUNT(*) as count 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        WHERE p.category_id IS NOT NULL AND c.id IS NULL
    """).fetchone()['count']
    
    if products_no_cat > 0:
        print(f"❌ {products_no_cat} products with invalid category references")
    else:
        print("✅ All products have valid category references")
    
    # Check for empty/invalid data
    empty_products = conn.execute("SELECT COUNT(*) as count FROM products WHERE name IS NULL OR name = ''").fetchone()['count']
    if empty_products > 0:
        print(f"❌ {empty_products} products with empty names")
    else:
        print("✅ All products have names")
    
    conn.close()

def analyze_routes():
    """Analyze Flask routes for duplicates"""
    print("\n=== ROUTE ANALYSIS ===")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all route decorators
    route_pattern = r"@app\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[[^\]]+\])?\)"
    routes = re.findall(route_pattern, content)
    
    print(f"📊 Found {len(routes)} routes:")
    
    # Check for duplicates
    route_counts = {}
    for route in routes:
        route_counts[route] = route_counts.get(route, 0) + 1
    
    duplicates = {route: count for route, count in route_counts.items() if count > 1}
    
    if duplicates:
        print("❌ Duplicate routes found:")
        for route, count in duplicates.items():
            print(f"  - {route}: {count} definitions")
    else:
        print("✅ No duplicate routes")
    
    # List all routes
    for route in sorted(set(routes)):
        methods = []
        # Find methods for this route
        pattern = rf"@app\.route\(['\"]{ re.escape(route) }['\"](?:,\s*methods=\[([^\]]+)\])?\)"
        matches = re.findall(pattern, content)
        if matches and matches[0]:
            methods = [m.strip('\'"') for m in matches[0].split(',')]
        else:
            methods = ['GET']
        print(f"  - {route} [{', '.join(methods)}]")

def check_vital_features():
    """Check if vital features are properly implemented"""
    print("\n=== VITAL FEATURES CHECK ===")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    features = {
        'add_to_cart': r"@app\.route\(['\"]\/add_to_cart['\"]",
        'add_to_wishlist': r"@app\.route\(['\"]\/add_to_wishlist['\"]",
        'checkout': r"@app\.route\(['\"]\/checkout['\"]",
        'place_order': r"@app\.route\(['\"]\/place_order['\"]",
        'my_orders': r"@app\.route\(['\"]\/my_orders['\"]",
        'order_detail': r"@app\.route\(['\"]\/order_detail",
        'admin_orders': r"@app\.route\(['\"]\/admin\/orders['\"]",
        'update_order_status': r"@app\.route\(['\"]\/admin\/update_order_status['\"]",
        'admin_users': r"@app\.route\(['\"]\/admin\/users['\"]",
        'admin_products': r"@app\.route\(['\"]\/admin\/products['\"]",
    }
    
    for feature, pattern in features.items():
        if re.search(pattern, content):
            print(f"✅ {feature} - Route found")
        else:
            print(f"❌ {feature} - Route missing")
    
    # Check for redirect to my_orders after place_order
    place_order_func = re.search(r"def place_order\(\):.*?(?=def|\Z)", content, re.DOTALL)
    if place_order_func:
        if "redirect(url_for('my_orders'))" in place_order_func.group():
            print("✅ place_order redirects to my_orders")
        else:
            print("❌ place_order does not redirect to my_orders")
    
    # Check for AJAX handling in add_to_cart
    add_to_cart_func = re.search(r"def add_to_cart\(\):.*?(?=def|\Z)", content, re.DOTALL)
    if add_to_cart_func:
        if "X-Requested-With" in add_to_cart_func.group():
            print("✅ add_to_cart has AJAX detection")
        else:
            print("❌ add_to_cart missing AJAX detection")

def check_templates():
    """Check template files for issues"""
    print("\n=== TEMPLATE ANALYSIS ===")
    
    template_dir = "templates"
    if not os.path.exists(template_dir):
        print("❌ Templates directory not found!")
        return
    
    templates = []
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                templates.append(os.path.join(root, file))
    
    print(f"📊 Found {len(templates)} template files:")
    
    required_templates = [
        'templates/cart.html',
        'templates/checkout.html',
        'templates/my_orders.html',
        'templates/order_detail.html',
        'templates/wishlist.html',
        'templates/admin/dashboard.html',
        'templates/admin/orders.html',
        'templates/admin/users.html',
        'templates/admin/products.html',
    ]
    
    for template in required_templates:
        if os.path.exists(template):
            print(f"✅ {template}")
        else:
            print(f"❌ {template} - Missing")
    
    # Check for common issues in templates
    for template in templates:
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for hardcoded currency symbols
        if '$' in content and template != 'templates/admin/analytics.html':
            print(f"⚠️  {template} contains $ symbol (should use INR filter)")

def cleanup_suggestions():
    """Provide cleanup suggestions"""
    print("\n=== CLEANUP SUGGESTIONS ===")
    
    suggestions = [
        "Remove duplicate route definitions",
        "Clean up orphaned database records",
        "Ensure all products have valid categories",
        "Verify all templates use INR currency filter",
        "Remove unused image files from static/uploads",
        "Clean up empty or test data",
        "Ensure consistent error handling",
        "Verify all AJAX endpoints return proper JSON",
    ]
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")

if __name__ == "__main__":
    print("🔍 MediPlant WebApp Analysis")
    print("=" * 50)
    
    analyze_database()
    analyze_routes()
    check_vital_features()
    check_templates()
    cleanup_suggestions()
    
    print("\n" + "=" * 50)
    print("✨ Analysis Complete!")
