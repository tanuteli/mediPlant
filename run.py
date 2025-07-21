# Main Application Entry Point for MediPlant

import os
from dotenv import load_dotenv
from flask_migrate import Migrate, upgrade
from app import create_app
from app.database import db
from app.models import User, Role, Category, Product, Order

# Load environment variables
load_dotenv()

# Create Flask application
config_name = os.getenv('FLASK_CONFIG', 'development')
app = create_app(config_name)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Role': Role,
        'Category': Category,
        'Product': Product,
        'Order': Order
    }

@app.cli.command()
def deploy():
    """Run deployment tasks"""
    # Create database tables
    db.create_all()
    
    # Create or update user roles
    Role.insert_roles()
    
    # Create default categories
    Category.insert_default_categories()
    
    print("Deployment completed successfully!")

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized!")

@app.cli.command()
def create_admin():
    """Create admin user"""
    from getpass import getpass
    
    email = input("Admin email: ")
    name = input("Admin name: ")
    password = getpass("Admin password: ")
    
    # Check if admin already exists
    if User.query.filter_by(email=email).first():
        print("User with this email already exists!")
        return
    
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        print("Admin role not found. Run 'flask deploy' first.")
        return
    
    admin_user = User(
        email=email,
        name=name,
        role=admin_role,
        is_active=True,
        email_verified=True
    )
    admin_user.set_password(password)
    
    db.session.add(admin_user)
    db.session.commit()
    
    print(f"Admin user '{name}' created successfully!")

@app.cli.command()
def seed_data():
    """Seed database with sample data"""
    from app.utils.seed_data import seed_sample_data
    seed_sample_data()
    print("Sample data seeded successfully!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
