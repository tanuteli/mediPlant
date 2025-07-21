# Database Seeding Utilities for MediPlant

from app import db
from app.models import Role, User, Category, Product, SupplierProfile
from werkzeug.security import generate_password_hash
from datetime import datetime
import uuid

def seed_sample_data():
    """Seed database with sample data for development/testing"""
    
    print("Seeding roles...")
    seed_roles()
    
    print("Seeding categories...")
    seed_categories()
    
    print("Seeding users...")
    seed_users()
    
    print("Seeding products...")
    seed_products()
    
    db.session.commit()
    print("Sample data seeded successfully!")

def seed_roles():
    """Create default roles"""
    roles = [
        {'name': 'admin', 'description': 'Administrator with full access'},
        {'name': 'supplier', 'description': 'Product supplier/vendor'},
        {'name': 'consumer', 'description': 'Regular customer/consumer'}
    ]
    
    for role_data in roles:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(**role_data)
            db.session.add(role)

def seed_categories():
    """Create sample product categories"""
    categories = [
        {
            'name': 'Medicinal Herbs',
            'slug': 'medicinal-herbs',
            'description': 'Fresh and dried medicinal herbs for health and wellness'
        },
        {
            'name': 'Herbal Supplements',
            'slug': 'herbal-supplements',
            'description': 'Processed herbal supplements and capsules'
        },
        {
            'name': 'Essential Oils',
            'slug': 'essential-oils',
            'description': 'Pure essential oils extracted from medicinal plants'
        },
        {
            'name': 'Herbal Teas',
            'slug': 'herbal-teas',
            'description': 'Therapeutic herbal tea blends'
        },
        {
            'name': 'Seeds & Saplings',
            'slug': 'seeds-saplings',
            'description': 'Seeds and saplings for growing medicinal plants'
        },
        {
            'name': 'Ayurvedic Products',
            'slug': 'ayurvedic-products',
            'description': 'Traditional Ayurvedic medicines and formulations'
        }
    ]
    
    for cat_data in categories:
        category = Category.query.filter_by(slug=cat_data['slug']).first()
        if not category:
            category = Category(**cat_data)
            db.session.add(category)

def seed_users():
    """Create sample users"""
    # Admin user
    admin_role = Role.query.filter_by(name='admin').first()
    admin = User.query.filter_by(email='admin@mediplant.com').first()
    if not admin:
        admin = User(
            email='admin@mediplant.com',
            name='System Administrator',
            role=admin_role,
            is_active=True,
            email_verified=True,
            created_at=datetime.utcnow()
        )
        admin.set_password('admin123')
        db.session.add(admin)
    
    # Supplier users
    supplier_role = Role.query.filter_by(name='supplier').first()
    suppliers = [
        {
            'email': 'supplier1@mediplant.com',
            'name': 'Green Herbs Supplier',
            'company': 'Green Herbs Pvt Ltd',
            'phone': '9876543210'
        },
        {
            'email': 'supplier2@mediplant.com',
            'name': 'Natural Remedies Co',
            'company': 'Natural Remedies Company',
            'phone': '9876543211'
        }
    ]
    
    for supplier_data in suppliers:
        supplier = User.query.filter_by(email=supplier_data['email']).first()
        if not supplier:
            supplier = User(
                email=supplier_data['email'],
                name=supplier_data['name'],
                phone=supplier_data['phone'],
                role=supplier_role,
                is_active=True,
                email_verified=True,
                created_at=datetime.utcnow()
            )
            supplier.set_password('supplier123')
            db.session.add(supplier)
            
            # Create supplier profile
            profile = SupplierProfile(
                user_id=supplier.id,
                company_name=supplier_data['company'],
                description=f"Professional supplier of medicinal plants and herbs",
                business_license='BL' + str(uuid.uuid4())[:8].upper(),
                gst_number='GST' + str(uuid.uuid4())[:10].upper(),
                is_verified=True
            )
            db.session.add(profile)
    
    # Consumer users
    consumer_role = Role.query.filter_by(name='consumer').first()
    consumers = [
        {
            'email': 'customer1@example.com',
            'name': 'John Doe',
            'phone': '9876543212'
        },
        {
            'email': 'customer2@example.com',
            'name': 'Jane Smith',
            'phone': '9876543213'
        }
    ]
    
    for consumer_data in consumers:
        consumer = User.query.filter_by(email=consumer_data['email']).first()
        if not consumer:
            consumer = User(
                email=consumer_data['email'],
                name=consumer_data['name'],
                phone=consumer_data['phone'],
                role=consumer_role,
                is_active=True,
                email_verified=True,
                created_at=datetime.utcnow()
            )
            consumer.set_password('customer123')
            db.session.add(consumer)

def seed_products():
    """Create sample products"""
    # Get categories and suppliers
    categories = Category.query.all()
    suppliers = User.query.join(Role).filter(Role.name == 'supplier').all()
    
    if not categories or not suppliers:
        print("Categories or suppliers not found. Skipping product seeding.")
        return
    
    products = [
        {
            'name': 'Organic Turmeric Powder',
            'description': 'Pure organic turmeric powder with high curcumin content. Known for its anti-inflammatory properties.',
            'price': 299.00,
            'weight': 500,
            'category': 'medicinal-herbs',
            'stock': 100,
            'benefits': 'Anti-inflammatory, Antioxidant, Immune booster'
        },
        {
            'name': 'Fresh Aloe Vera Gel',
            'description': 'Fresh aloe vera gel extracted from organic aloe vera plants. Great for skin care.',
            'price': 149.00,
            'weight': 200,
            'category': 'medicinal-herbs',
            'stock': 50,
            'benefits': 'Skin healing, Moisturizing, Anti-bacterial'
        },
        {
            'name': 'Ashwagandha Capsules',
            'description': 'Premium ashwagandha root extract capsules for stress relief and energy.',
            'price': 599.00,
            'weight': 100,
            'category': 'herbal-supplements',
            'stock': 75,
            'benefits': 'Stress relief, Energy boost, Immunity support'
        },
        {
            'name': 'Neem Oil',
            'description': 'Pure cold-pressed neem oil with natural antibacterial properties.',
            'price': 199.00,
            'weight': 100,
            'category': 'essential-oils',
            'stock': 30,
            'benefits': 'Antibacterial, Antifungal, Skin care'
        },
        {
            'name': 'Chamomile Tea',
            'description': 'Organic chamomile tea blend for relaxation and better sleep.',
            'price': 249.00,
            'weight': 100,
            'category': 'herbal-teas',
            'stock': 60,
            'benefits': 'Relaxation, Better sleep, Digestive health'
        },
        {
            'name': 'Tulsi Seeds',
            'description': 'High-quality tulsi (holy basil) seeds for growing your own medicinal plants.',
            'price': 99.00,
            'weight': 10,
            'category': 'seeds-saplings',
            'stock': 200,
            'benefits': 'Immunity booster, Respiratory health, Stress relief'
        }
    ]
    
    for i, product_data in enumerate(products):
        # Check if product already exists
        existing_product = Product.query.filter_by(name=product_data['name']).first()
        if existing_product:
            continue
        
        # Get category
        category = next((c for c in categories if c.slug == product_data['category']), categories[0])
        
        # Assign to supplier (cycle through suppliers)
        supplier = suppliers[i % len(suppliers)]
        
        # Create product
        product = Product(
            name=product_data['name'],
            slug=product_data['name'].lower().replace(' ', '-'),
            description=product_data['description'],
            short_description=product_data['description'][:100] + '...',
            price=product_data['price'],
            weight=product_data['weight'],
            category_id=category.id,
            supplier_id=supplier.id,
            stock_quantity=product_data['stock'],
            sku=f"MP{datetime.now().strftime('%Y%m%d')}{i+1:03d}",
            is_active=True,
            health_benefits=product_data['benefits'],
            created_at=datetime.utcnow()
        )
        
        db.session.add(product)

def clear_sample_data():
    """Clear all sample data (for testing purposes)"""
    print("Clearing sample data...")
    
    # Clear in reverse order of dependencies
    Product.query.delete()
    SupplierProfile.query.delete()
    User.query.delete()
    Category.query.delete()
    Role.query.delete()
    
    db.session.commit()
    print("Sample data cleared!")

def reset_database():
    """Reset database with fresh sample data"""
    clear_sample_data()
    seed_sample_data()
