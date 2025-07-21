#!/usr/bin/env python3
"""
MediPlant Setup Script
Automated setup for the MediPlant e-commerce platform
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🌿 MediPlant - E-Commerce Platform Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")
    print()

def create_virtual_environment():
    """Create and activate virtual environment"""
    print("🔧 Creating virtual environment...")
    
    # Check if venv already exists
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
    else:
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Virtual environment created")
        except subprocess.CalledProcessError:
            print("❌ Failed to create virtual environment")
            sys.exit(1)
    
    # Provide activation instructions
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
    else:  # macOS/Linux
        activate_cmd = "source venv/bin/activate"
    
    print(f"💡 To activate: {activate_cmd}")
    print()

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:  # macOS/Linux
        pip_path = os.path.join("venv", "bin", "pip")
    
    if not os.path.exists(pip_path):
        print("⚠️  Virtual environment not activated. Please activate it first.")
        return
    
    try:
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("💡 Make sure you've activated the virtual environment")
    except FileNotFoundError:
        print("❌ requirements.txt not found")
    print()

def create_env_file():
    """Create .env file with default configuration"""
    print("⚙️  Creating environment configuration...")
    
    env_content = """# MediPlant Environment Configuration

# Database Configuration
DATABASE_URL=sqlite:///mediplant.db

# Security Keys (Change these in production!)
SECRET_KEY=dev-secret-key-change-in-production
WTF_CSRF_SECRET_KEY=dev-csrf-key-change-in-production

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Email Configuration (Optional - for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Payment Gateway Configuration (Optional)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-secret
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-secret

# File Upload Configuration
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,webp

# Security Settings
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
PERMANENT_SESSION_LIFETIME=86400
"""
    
    if os.path.exists(".env"):
        print("✅ .env file already exists")
    else:
        try:
            with open(".env", "w") as f:
                f.write(env_content)
            print("✅ .env file created with default configuration")
            print("💡 Please update the configuration values as needed")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
    print()

def setup_database():
    """Initialize SQLite database"""
    print("🗄️  Setting up database...")
    
    db_path = "mediplant.db"
    
    try:
        # Create database file if it doesn't exist
        if not os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            conn.close()
            print("✅ SQLite database file created")
        else:
            print("✅ Database file already exists")
        
        print("💡 Database tables will be created when you first run the application")
        
    except Exception as e:
        print(f"❌ Failed to setup database: {e}")
    print()

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directory structure...")
    
    directories = [
        "app/static/uploads",
        "app/static/uploads/products",
        "app/static/uploads/users",
        "app/static/uploads/temp",
        "logs",
        "backups"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {directory}")
        except Exception as e:
            print(f"❌ Failed to create {directory}: {e}")
    print()

def create_sample_data_script():
    """Create a script to generate sample data"""
    print("📊 Creating sample data script...")
    
    sample_script = """#!/usr/bin/env python3
'''
Sample Data Generator for MediPlant
Run this script to populate the database with sample data for testing
'''

from app import create_app, db
from app.models import User, Category, Product
from werkzeug.security import generate_password_hash
import random
from datetime import datetime

def create_sample_data():
    '''Create sample data for testing'''
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created!")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@mediplant.com',
            password_hash=generate_password_hash('Admin@123'),
            role='admin',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        
        # Create sample supplier
        supplier = User(
            username='supplier1',
            email='supplier@mediplant.com',
            password_hash=generate_password_hash('Supplier@123'),
            role='supplier',
            is_active=True,
            is_approved=True,
            created_at=datetime.utcnow()
        )
        db.session.add(supplier)
        
        # Create sample consumer
        consumer = User(
            username='consumer1',
            email='consumer@mediplant.com',
            password_hash=generate_password_hash('Consumer@123'),
            role='consumer',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(consumer)
        
        # Create sample categories
        categories = [
            'Medicinal Herbs',
            'Ayurvedic Plants',
            'Essential Oil Plants',
            'Therapeutic Roots',
            'Healing Leaves',
            'Herbal Seeds'
        ]
        
        for cat_name in categories:
            category = Category(
                name=cat_name,
                description=f'High-quality {cat_name.lower()} for wellness and health',
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(category)
        
        # Commit users and categories first
        db.session.commit()
        print("Sample users and categories created!")
        
        # Create sample products
        sample_products = [
            ('Turmeric Rhizome', 'Fresh organic turmeric with anti-inflammatory properties', 299.99),
            ('Ashwagandha Root', 'Premium ashwagandha for stress relief and vitality', 499.99),
            ('Neem Leaves', 'Pure neem leaves with antibacterial properties', 199.99),
            ('Tulsi Plant', 'Holy basil plant for respiratory health', 149.99),
            ('Ginger Root', 'Fresh ginger root for digestive health', 179.99),
            ('Aloe Vera Plant', 'Live aloe vera plant for skin care', 249.99),
        ]
        
        for i, (name, desc, price) in enumerate(sample_products):
            product = Product(
                name=name,
                description=desc,
                price=price,
                stock_quantity=random.randint(10, 100),
                category_id=random.randint(1, len(categories)),
                supplier_id=supplier.id,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(product)
        
        db.session.commit()
        print("Sample products created!")
        
        print("\\n✅ Sample data created successfully!")
        print("\\n📋 Default login credentials:")
        print("   Admin: admin@mediplant.com / Admin@123")
        print("   Supplier: supplier@mediplant.com / Supplier@123") 
        print("   Consumer: consumer@mediplant.com / Consumer@123")

if __name__ == '__main__':
    create_sample_data()
"""
    
    try:
        with open("create_sample_data.py", "w") as f:
            f.write(sample_script)
        print("✅ Sample data script created: create_sample_data.py")
        print("💡 Run 'python create_sample_data.py' to populate database with test data")
    except Exception as e:
        print(f"❌ Failed to create sample data script: {e}")
    print()

def print_next_steps():
    """Print next steps for the user"""
    print("🎉 Setup completed successfully!")
    print()
    print("📋 Next Steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # macOS/Linux
        print("   source venv/bin/activate")
    
    print()
    print("2. Create database tables and sample data:")
    print("   python create_sample_data.py")
    print()
    print("3. Start the development server:")
    print("   python run.py")
    print()
    print("4. Open your browser and visit:")
    print("   http://localhost:5000")
    print()
    print("📖 For more information, see README.md")
    print("🐛 Report issues at: https://github.com/tanuteli/mediPlant/issues")
    print()

def main():
    """Main setup function"""
    print_header()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    check_python_version()
    create_virtual_environment()
    create_env_file()
    setup_database()
    create_directories()
    create_sample_data_script()
    print_next_steps()

if __name__ == "__main__":
    main()
