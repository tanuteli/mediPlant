# Database Models for MediPlant E-Commerce Platform

from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db
import enum

# Enums for database constraints
class UserRole(enum.Enum):
    ADMIN = "admin"
    SUPPLIER = "supplier"
    CONSUMER = "consumer"

class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(enum.Enum):
    RAZORPAY = "razorpay"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    COD = "cod"

# Core Models
class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(UserRole), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='role', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    profile_image = db.Column(db.String(255))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    supplier_profile = db.relationship('SupplierProfile', backref='user', uselist=False)
    addresses = db.relationship('UserAddress', backref='user', lazy=True)
    products = db.relationship('Product', backref='supplier', lazy=True)
    orders_as_customer = db.relationship('Order', foreign_keys='Order.user_id', backref='customer', lazy=True)
    orders_as_supplier = db.relationship('Order', foreign_keys='Order.supplier_id', backref='supplier', lazy=True)
    reviews = db.relationship('ProductReview', backref='user', lazy=True)
    cart_items = db.relationship('ShoppingCart', backref='user', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_role_name(self):
        """Get user role name"""
        return self.role.name.value if self.role else None
    
    def is_admin(self):
        """Check if user is admin"""
        return self.get_role_name() == 'admin'
    
    def is_supplier(self):
        """Check if user is supplier"""
        return self.get_role_name() == 'supplier'
    
    def is_consumer(self):
        """Check if user is consumer"""
        return self.get_role_name() == 'consumer'

class SupplierProfile(db.Model):
    __tablename__ = 'supplier_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    business_name = db.Column(db.String(150), nullable=False)
    business_license = db.Column(db.String(100))
    tax_number = db.Column(db.String(50))
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100), default='India')
    is_approved = db.Column(db.Boolean, default=False)
    approval_date = db.Column(db.DateTime)
    rating = db.Column(db.Numeric(3, 2), default=0.00)
    total_sales = db.Column(db.Numeric(12, 2), default=0.00)
    commission_rate = db.Column(db.Numeric(5, 2), default=10.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserAddress(db.Model):
    __tablename__ = 'user_addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address_type = db.Column(db.Enum('home', 'work', 'other', name='address_type'), default='home')
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), default='India')
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Product Models
class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for subcategories
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True)
    scientific_name = db.Column(db.String(150))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sku = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    benefits = db.Column(db.Text)
    usage_instructions = db.Column(db.Text)
    care_instructions = db.Column(db.Text)
    warnings = db.Column(db.Text)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_price = db.Column(db.Numeric(10, 2))
    stock_quantity = db.Column(db.Integer, default=0)
    min_order_quantity = db.Column(db.Integer, default=1)
    max_order_quantity = db.Column(db.Integer, default=999)
    weight = db.Column(db.Numeric(8, 2))  # in grams
    dimensions = db.Column(db.String(100))  # Length x Width x Height
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(500))
    views_count = db.Column(db.Integer, default=0)
    sales_count = db.Column(db.Integer, default=0)
    rating_average = db.Column(db.Numeric(3, 2), default=0.00)
    rating_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images = db.relationship('ProductImage', backref='product', lazy=True)
    variants = db.relationship('ProductVariant', backref='product', lazy=True)
    attributes = db.relationship('ProductAttribute', backref='product', lazy=True)
    reviews = db.relationship('ProductReview', backref='product', lazy=True)
    cart_items = db.relationship('ShoppingCart', backref='product', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def get_current_price(self):
        """Get current effective price"""
        return self.discount_price if self.discount_price else self.base_price
    
    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.discount_price and self.discount_price < self.base_price:
            return round(((self.base_price - self.discount_price) / self.base_price) * 100, 2)
        return 0

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(255))
    is_primary = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProductVariant(db.Model):
    __tablename__ = 'product_variants'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Small Pot", "Seeds Pack"
    sku = db.Column(db.String(100), unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_price = db.Column(db.Numeric(10, 2))
    stock_quantity = db.Column(db.Integer, default=0)
    weight = db.Column(db.Numeric(8, 2))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProductAttribute(db.Model):
    __tablename__ = 'product_attributes'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    attribute_name = db.Column(db.String(100), nullable=False)
    attribute_value = db.Column(db.String(255), nullable=False)

# Shopping Models
class ShoppingCart(db.Model):
    __tablename__ = 'shopping_cart'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', 'variant_id', name='unique_cart_item'),)

class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_wishlist_item'),)

# Order Models
class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = db.Column(db.Enum(PaymentMethod), default=PaymentMethod.COD)
    payment_id = db.Column(db.String(255))  # Gateway transaction ID
    
    # Pricing
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    shipping_amount = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Addresses (stored as JSON)
    shipping_address = db.Column(db.JSON)
    billing_address = db.Column(db.JSON)
    
    # Tracking
    tracking_number = db.Column(db.String(100))
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Notes
    order_notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True)
    tracking_history = db.relationship('OrderTracking', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    product_name = db.Column(db.String(200))  # Store product name at time of order
    product_sku = db.Column(db.String(100))
    supplier_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Denormalized for easier queries

class OrderTracking(db.Model):
    __tablename__ = 'order_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Review Models
class ProductReview(db.Model):
    __tablename__ = 'product_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))  # Link to actual purchase
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    title = db.Column(db.String(200))
    comment = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)  # Verified purchase
    is_approved = db.Column(db.Boolean, default=True)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', 'order_id', name='unique_user_product_review'),
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range')
    )

# Initialize database with default data
def init_db():
    """Initialize database with default roles and admin user"""
    db.create_all()
    
    # Create default roles
    if not Role.query.first():
        admin_role = Role(name=UserRole.ADMIN, description='Platform Administrator')
        supplier_role = Role(name=UserRole.SUPPLIER, description='Product Supplier/Vendor')
        consumer_role = Role(name=UserRole.CONSUMER, description='Customer/Buyer')
        
        db.session.add_all([admin_role, supplier_role, consumer_role])
        db.session.commit()
    
    # Create default admin user
    if not User.query.filter_by(email='admin@mediplant.com').first():
        admin_role = Role.query.filter_by(name=UserRole.ADMIN).first()
        admin_user = User(
            name='System Admin',
            email='admin@mediplant.com',
            role_id=admin_role.id,
            is_verified=True
        )
        admin_user.set_password('Admin@123')
        
        db.session.add(admin_user)
        db.session.commit()
