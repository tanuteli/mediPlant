#!/usr/bin/env python3
"""
Sample data creation script for MediPlant webapp
Creates demo users, categories, products, and other data
"""

import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def hash_password(password):
    """Hash password using werkzeug (same as Flask app)"""
    return generate_password_hash(password)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('mediplant.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_sample_data():
    """Create all sample data"""
    conn = get_db_connection()
    
    try:
        print("🌱 Creating sample data for MediPlant...")
        
        # Clear existing data
        print("📝 Clearing existing data...")
        tables = ['cart', 'reviews', 'orders', 'products', 'categories', 'users']
        for table in tables:
            try:
                conn.execute(f'DELETE FROM {table}')
            except sqlite3.OperationalError:
                pass  # Table might not exist yet
        
        # Create demo users
        print("👥 Creating demo users...")
        demo_users = [
            {
                'username': 'admin',
                'email': 'admin@mediplant.com',
                'password': hash_password('admin123'),
                'full_name': 'Admin User',
                'role': 'admin',
                'is_active': 1,
                'phone': '+1-555-0100',
                'address': '123 Admin Street, Admin City, AC 12345'
            },
            {
                'username': 'demo',
                'email': 'demo@mediplant.com', 
                'password': hash_password('demo123'),
                'full_name': 'Demo Customer',
                'role': 'user',
                'is_active': 1,
                'phone': '+1-555-0101',
                'address': '456 Customer Lane, Demo City, DC 67890'
            },
            {
                'username': 'johndoe',
                'email': 'john@example.com',
                'password': hash_password('password123'),
                'full_name': 'John Doe',
                'role': 'user',
                'is_active': 1,
                'phone': '+1-555-0102',
                'address': '789 User Boulevard, Example City, EC 11111'
            },
            {
                'username': 'janedoe',
                'email': 'jane@example.com',
                'password': hash_password('password123'),
                'full_name': 'Jane Doe',
                'role': 'user',
                'is_active': 1,
                'phone': '+1-555-0103',
                'address': '321 Demo Road, Sample City, SC 22222'
            }
        ]
        
        for user in demo_users:
            conn.execute('''
                INSERT INTO users (username, email, password_hash, full_name, role, is_active, 
                                 phone, address, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user['username'], user['email'], user['password'], user['full_name'],
                  user['role'], user['is_active'], user['phone'], user['address'], 
                  datetime.now()))
        
        print(f"✅ Created {len(demo_users)} demo users")
        
        # Create categories
        print("📂 Creating product categories...")
        categories = [
            {
                'name': 'Ayurvedic Herbs',
                'description': 'Traditional Indian medicinal herbs used in Ayurveda for thousands of years',
                'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80'
            },
            {
                'name': 'Adaptogenic Herbs',
                'description': 'Herbs that help the body adapt to stress and promote balance',
                'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80'
            },
            {
                'name': 'Herbal Teas & Kadhas',
                'description': 'Traditional Indian healing teas and kadhas for daily wellness',
                'image_url': 'https://images.unsplash.com/photo-1563414083-40b1e0abe313?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80'
            },
            {
                'name': 'Beauty & Skincare Herbs',
                'description': 'Natural Indian beauty herbs and ingredients for skin and hair care',
                'image_url': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80'
            },
            {
                'name': 'Digestive & Wellness',
                'description': 'Herbs for digestive health and overall wellness support',
                'image_url': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80'
            }
        ]
        
        for category in categories:
            conn.execute('''
                INSERT INTO categories (name, description, image_url, created_at)
                VALUES (?, ?, ?, ?)
            ''', (category['name'], category['description'], category['image_url'], datetime.now()))
        
        print(f"✅ Created {len(categories)} categories")
        
        # Create sample products
        print("🌿 Creating sample products...")
        sample_products = [
            {
                'name': 'Organic Turmeric (Haldi) Root',
                'description': 'Fresh organic turmeric root with powerful anti-inflammatory properties from Kerala farms',
                'detailed_description': 'Our premium organic turmeric root is sourced directly from certified organic farms in Kerala. Known for its active compound curcumin, this golden herb has been used for thousands of years in Ayurveda for its anti-inflammatory, antioxidant, and healing properties. Perfect for cooking, making golden milk, or traditional remedies.',
                'price': 299.99,
                'category_id': 1,
                'image_url': 'https://images.unsplash.com/photo-1518799175676-a0fed7996acb?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'stock_quantity': 50,
                'benefits': 'Anti-inflammatory, antioxidant, supports joint health, boosts immunity, aids digestion',
                'usage_instructions': 'Can be used fresh, dried, or powdered. Add to cooking, make golden milk, or prepare traditional kadha.',
                'warnings': 'May interact with blood thinners. Consult physician if pregnant or nursing. Avoid if allergic to turmeric.'
            },
            {
                'name': 'Fresh Ginger (Adrak) Root',
                'description': 'Organic ginger root from Himachal Pradesh, known for digestive and anti-nausea properties',
                'detailed_description': 'Premium quality fresh ginger root from the hills of Himachal Pradesh. This warming herb is a staple in Indian kitchens and Ayurvedic medicine, renowned for its digestive benefits and natural anti-nausea properties.',
                'price': 199.49,
                'category_id': 5,
                'image_url': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'stock_quantity': 75,
                'benefits': 'Aids digestion, reduces nausea, anti-inflammatory, warming properties, supports circulation',
                'usage_instructions': 'Use fresh in cooking, make ginger tea (adrak chai), or juice for remedies. Ideal for making traditional kadha.',
                'warnings': 'May increase bleeding risk. Avoid large amounts if on blood thinners. Consult doctor if pregnant.'
            },
            {
                'name': 'Aloe Vera (Ghritkumari) Plant',
                'description': 'Living aloe vera plant for fresh gel extraction and traditional Ayurvedic use',
                'detailed_description': 'Beautiful living aloe vera plant that provides fresh gel for topical and internal use. Known in Ayurveda as Ghritkumari, this succulent has cooling properties and is excellent for skin care and digestive health.',
                'price': 399.99,
                'category_id': 4,
                'image_url': 'https://images.unsplash.com/photo-1509423350716-97f2360af57e?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'stock_quantity': 30,
                'benefits': 'Soothes burns, heals cuts, moisturizes skin, aids digestion, cooling properties, purifies air',
                'usage_instructions': 'Break off leaf and apply gel directly to skin. Can be consumed in small amounts for digestive health. Water plant weekly.',
                'warnings': 'For external use primarily. Consult Ayurvedic practitioner before internal use. May cause allergic reactions in some.'
            },
            {
                'name': 'Lavender (Ustukhuddus) Plant',
                'description': 'Aromatic lavender plant for relaxation, stress relief, and natural fragrance',
                'detailed_description': 'Fragrant lavender plant that provides natural aromatherapy benefits. Used in both Ayurveda and aromatherapy for its calming properties. Perfect for creating a peaceful environment and natural stress relief.',
                'price': 499.99,
                'category_id': 3,
                'image_url': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'stock_quantity': 25,
                'benefits': 'Promotes relaxation, improves sleep quality, reduces stress, natural insect repellent, aromatherapy',
                'usage_instructions': 'Harvest flowers for tea or essential oil. Place near bedside for better sleep. Requires full sun and good drainage.',
                'warnings': 'Generally safe, but may cause skin irritation in sensitive individuals. Not recommended during pregnancy.'
            },
            {
                'name': 'Holy Basil (Tulsi) Plant',
                'description': 'Sacred Tulsi plant, the queen of herbs in Ayurveda for stress relief and immunity',
                'detailed_description': 'Holy Basil, known as Tulsi in India, is considered the queen of herbs in Ayurveda. This sacred plant is revered for its adaptogenic properties and is used daily in Indian households for health and spiritual purposes.',
                'price': 349.99,
                'category_id': 1,
                'image_url': 'https://images.unsplash.com/photo-1574263867128-5ac2b8511b4e?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'stock_quantity': 40,
                'benefits': 'Reduces stress, supports immune system, adaptogenic properties, respiratory health, sacred herb',
                'usage_instructions': 'Make Tulsi tea with fresh or dried leaves. Can be chewed fresh in morning. Use in daily prayers and meditation.',
                'warnings': 'May lower blood sugar. Monitor levels if diabetic. Consult doctor if on medication.'
            },
            {
                'name': 'Ashwagandha (Winter Cherry) Root',
                'description': 'Premium Ashwagandha root powder from Rajasthan for strength and vitality',
                'detailed_description': 'Premium Ashwagandha root powder sourced from the arid regions of Rajasthan. Known as Indian Winter Cherry, this powerful adaptogen is one of the most important herbs in Ayurveda for building strength and managing stress.',
                'price': 899.99,
                'category_id': 2,
                'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'stock_quantity': 35,
                'benefits': 'Reduces stress and anxiety, boosts energy, supports cognitive function, enhances strength, improves sleep',
                'usage_instructions': 'Mix 1-2 teaspoons with warm milk or water. Best taken at bedtime. Can be mixed with honey or ghee.',
                'warnings': 'Not recommended during pregnancy or breastfeeding. May interact with medications. Consult Ayurvedic doctor.'
            },
            {
                'name': 'Brahmi (Bacopa Monnieri)',
                'description': 'Brahmi herb for memory enhancement and cognitive support from Uttarakhand',
                'detailed_description': 'Pure Brahmi (Bacopa Monnieri) sourced from the pristine regions of Uttarakhand. This brain tonic is highly valued in Ayurveda for enhancing memory, concentration, and overall cognitive function.',
                'price': 699.99,
                'category_id': 1,
                'image_url': 'https://images.unsplash.com/photo-1566158893574-24498dc7d86d?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'stock_quantity': 20,
                'benefits': 'Enhances memory, improves concentration, supports cognitive function, reduces mental fatigue, brain tonic',
                'usage_instructions': 'Take as powder with milk or honey. Can be made into herbal tea. Best taken regularly for sustained benefits.',
                'warnings': 'May cause mild stomach upset initially. Consult healthcare provider if taking medications for depression or anxiety.'
            },
            {
                'name': 'Chamomile (Babuna) Flowers',
                'description': 'Dried chamomile flowers for soothing tea and relaxation',
                'detailed_description': 'Premium dried chamomile flowers perfect for making calming tea. Known in traditional Indian medicine as Babuna, these flowers are renowned for their gentle sedative properties and digestive benefits.',
                'price': 399.99,
                'category_id': 3,
                'image_url': 'https://images.unsplash.com/photo-1563414083-40b1e0abe313?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'stock_quantity': 60,
                'benefits': 'Promotes restful sleep, calms nerves, aids digestion, anti-inflammatory, soothes skin',
                'usage_instructions': 'Steep 1-2 teaspoons in hot water for 5-10 minutes for tea. Can be used for steam inhalation or face wash.',
                'warnings': 'May cause allergic reactions in people sensitive to plants in the daisy family. Avoid if allergic to ragweed.'
            },
            {
                'name': 'Neem (Margosa) Leaves',
                'description': 'Fresh neem leaves for natural purification and traditional remedies',
                'detailed_description': 'Fresh neem leaves from organically grown neem trees. Neem is called the village pharmacy in India due to its numerous therapeutic properties. These bitter leaves are excellent for natural purification.',
                'price': 249.99,
                'category_id': 4,
                'image_url': 'https://images.unsplash.com/photo-1600166442533-f7d3c3463bdb?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'stock_quantity': 45,
                'benefits': 'Natural purifier, supports skin health, antimicrobial properties, supports oral health, traditional detox',
                'usage_instructions': 'Chew 2-3 fresh leaves on empty stomach. Can be boiled for face wash or hair rinse. Use in traditional remedies.',
                'warnings': 'Very bitter taste. Not recommended during pregnancy. May lower blood sugar levels. Use in moderation.'
            },
            {
                'name': 'Amla (Indian Gooseberry)',
                'description': 'Fresh Amla fruits rich in Vitamin C and traditional Ayurvedic superfood',
                'detailed_description': 'Fresh Amla (Indian Gooseberry) fruits from organic orchards. This superfruit is one of the richest sources of Vitamin C and is considered a rasayana (rejuvenative) in Ayurveda.',
                'price': 199.99,
                'category_id': 1,
                'image_url': 'https://images.unsplash.com/photo-1611080148122-1348ad0b5d4b?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'stock_quantity': 55,
                'benefits': 'Rich in Vitamin C, boosts immunity, supports hair health, anti-aging properties, digestive aid',
                'usage_instructions': 'Eat fresh, make juice, or prepare traditional pickles and preserves. Can be dried and powdered for daily use.',
                'warnings': 'Very sour taste. May cause acidity in sensitive individuals. Start with small amounts.'
            }
        ]
        
        for product in sample_products:
            conn.execute('''
                INSERT INTO products (name, description, detailed_description, price, category_id,
                                    image_url, stock_quantity, benefits, usage_instructions, warnings, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (product['name'], product['description'], product['detailed_description'],
                  product['price'], product['category_id'], product['image_url'], 
                  product['stock_quantity'], product['benefits'], product['usage_instructions'],
                  product['warnings'], datetime.now()))
        
        print(f"✅ Created {len(sample_products)} sample products")
        
        # Create sample reviews
        print("⭐ Creating sample reviews...")
        review_texts = [
            "Excellent quality! Very fresh and potent. Highly recommended.",
            "Great product, fast shipping. Will order again.",
            "Amazing results! I can really feel the difference.",
            "Good quality but shipping was a bit slow.",
            "Perfect for my daily wellness routine. Love it!",
            "High quality product at a reasonable price.",
            "Exactly as described. Very satisfied with purchase.",
            "Fresh and authentic. Great customer service too!",
            "Been using this for weeks now. Excellent results.",
            "Good value for money. Quality is consistent."
        ]
        
        for i in range(1, 9):  # Reviews for first 8 products
            for j in range(random.randint(2, 5)):  # 2-5 reviews per product
                rating = random.choice([4, 4, 5, 5, 5, 3, 4])  # Weighted towards higher ratings
                review_text = random.choice(review_texts)
                reviewer_id = random.choice([2, 3, 4])  # Demo users (not admin)
                
                conn.execute('''
                    INSERT INTO reviews (product_id, user_id, rating, review_text, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (i, reviewer_id, rating, review_text, 
                      datetime.now() - timedelta(days=random.randint(1, 30))))
        
        print("✅ Created sample reviews")
        
        # Create sample cart items for demo user
        print("🛒 Creating sample cart items...")
        demo_user_id = 2  # Demo user
        cart_items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 3, 'quantity': 1},
            {'product_id': 5, 'quantity': 1}
        ]
        
        for item in cart_items:
            conn.execute('''
                INSERT INTO cart (user_id, product_id, quantity, created_at)
                VALUES (?, ?, ?, ?)
            ''', (demo_user_id, item['product_id'], item['quantity'], datetime.now()))
        
        print("✅ Created sample cart items")
        
        # Create sample orders
        print("📦 Creating sample orders...")
        sample_orders = [
            {
                'user_id': 2,
                'total_amount': 48.97,
                'status': 'completed',
                'full_name': 'Demo Customer',
                'email': 'demo@mediplant.com',
                'phone': '+91-9876543210',
                'address': '456 MG Road, Bangalore, Karnataka 560001',
                'payment_method': 'upi',
                'created_at': datetime.now() - timedelta(days=7)
            },
            {
                'user_id': 3,
                'total_amount': 37.98,
                'status': 'processing',
                'full_name': 'John Doe',
                'email': 'john@example.com',
                'phone': '+91-9876543211',
                'address': '789 Connaught Place, New Delhi, Delhi 110001',
                'payment_method': 'razorpay',
                'created_at': datetime.now() - timedelta(days=2)
            },
            {
                'user_id': 4,
                'total_amount': 67.97,
                'status': 'shipped',
                'full_name': 'Jane Doe',
                'email': 'jane@example.com',
                'phone': '+91-9876543213',
                'address': '321 Residency Road, Chennai, Tamil Nadu 600001',
                'payment_method': 'cash_on_delivery',
                'created_at': datetime.now() - timedelta(days=3)
            }
        ]
        
        for order in sample_orders:
            conn.execute('''
                INSERT INTO orders (user_id, total_amount, status, shipping_address, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (order['user_id'], order['total_amount'], order['status'], order['address'],
                  order['created_at']))
        
        print("✅ Created sample orders")
        
        conn.commit()
        
        print("\n🎉 Sample data creation completed successfully!")
        print("\n📋 Demo Login Credentials:")
        print("=" * 50)
        print("🔑 ADMIN ACCESS:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   URL: http://localhost:5000/admin")
        print()
        print("👤 CUSTOMER ACCESS:")
        print("   Username: demo") 
        print("   Password: demo123")
        print("   URL: http://localhost:5000/login")
        print("=" * 50)
        print("\n🚀 Ready to start! Run 'python app.py' to launch the webapp.")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    create_sample_data()
