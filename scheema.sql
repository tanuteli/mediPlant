-- schema.sql — Complete database schema for MediPlant Multi-Vendor E-Commerce Platform
-- Supports Admin, Supplier, Consumer roles with full marketplace functionality

-- ================================
-- CORE USER MANAGEMENT TABLES
-- ================================

CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name ENUM('admin', 'supplier', 'consumer') UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    profile_image VARCHAR(255),
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Supplier-specific profile information
CREATE TABLE supplier_profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE,
    business_name VARCHAR(150) NOT NULL,
    business_license VARCHAR(100),
    tax_number VARCHAR(50),
    description TEXT,
    website VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'India',
    is_approved BOOLEAN DEFAULT FALSE,
    approval_date TIMESTAMP NULL,
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_sales DECIMAL(12,2) DEFAULT 0.00,
    commission_rate DECIMAL(5,2) DEFAULT 10.00, -- Platform commission percentage
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Consumer addresses for shipping
CREATE TABLE user_addresses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    address_type ENUM('home', 'work', 'other') DEFAULT 'home',
    full_name VARCHAR(100),
    phone VARCHAR(20),
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) DEFAULT 'India',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Email verification tokens
CREATE TABLE email_verifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    token VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Password reset tokens
CREATE TABLE password_resets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    token VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ================================
-- PRODUCT CATALOG TABLES
-- ================================

CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) UNIQUE,
    description TEXT,
    parent_id INT NULL, -- For subcategories
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);

CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE,
    scientific_name VARCHAR(150),
    category_id INT,
    supplier_id INT,
    sku VARCHAR(100) UNIQUE,
    description TEXT,
    short_description VARCHAR(500),
    benefits TEXT,
    usage_instructions TEXT,
    care_instructions TEXT,
    warnings TEXT,
    base_price DECIMAL(10, 2) NOT NULL,
    discount_price DECIMAL(10, 2) NULL,
    stock_quantity INT DEFAULT 0,
    min_order_quantity INT DEFAULT 1,
    max_order_quantity INT DEFAULT 999,
    weight DECIMAL(8,2), -- in grams
    dimensions VARCHAR(100), -- Length x Width x Height
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    meta_title VARCHAR(200),
    meta_description VARCHAR(500),
    views_count INT DEFAULT 0,
    sales_count INT DEFAULT 0,
    rating_average DECIMAL(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (supplier_id) REFERENCES users(id),
    INDEX idx_supplier_id (supplier_id),
    INDEX idx_category_id (category_id),
    INDEX idx_slug (slug),
    INDEX idx_is_active (is_active)
);

CREATE TABLE product_images (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    image_url VARCHAR(255) NOT NULL,
    alt_text VARCHAR(255),
    is_primary BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Product variants (different sizes, forms, etc.)
CREATE TABLE product_variants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    name VARCHAR(100) NOT NULL, -- e.g., "Small Pot", "Seeds Pack", "Dried Powder"
    sku VARCHAR(100) UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    discount_price DECIMAL(10, 2) NULL,
    stock_quantity INT DEFAULT 0,
    weight DECIMAL(8,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Product attributes (organic, region, harvest date, etc.)
CREATE TABLE product_attributes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    attribute_name VARCHAR(100) NOT NULL,
    attribute_value VARCHAR(255) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ================================
-- SHOPPING & ORDER MANAGEMENT
-- ================================

CREATE TABLE shopping_cart (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    product_id INT,
    variant_id INT NULL,
    quantity INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE CASCADE,
    UNIQUE KEY unique_cart_item (user_id, product_id, variant_id)
);

CREATE TABLE wishlists (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    product_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_wishlist_item (user_id, product_id)
);

CREATE TABLE coupons (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100),
    description TEXT,
    discount_type ENUM('percentage', 'fixed') NOT NULL,
    discount_value DECIMAL(10, 2) NOT NULL,
    minimum_amount DECIMAL(10, 2) DEFAULT 0,
    maximum_discount DECIMAL(10, 2) NULL,
    usage_limit INT NULL, -- NULL = unlimited
    used_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    valid_from DATETIME NOT NULL,
    valid_until DATETIME NOT NULL,
    created_by INT, -- Admin user who created this
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INT,
    supplier_id INT, -- Orders are per supplier
    status ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded') DEFAULT 'pending',
    payment_status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
    payment_method ENUM('razorpay', 'paypal', 'stripe', 'cod') DEFAULT 'cod',
    payment_id VARCHAR(255), -- Gateway transaction ID
    
    -- Pricing
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    shipping_amount DECIMAL(10, 2) DEFAULT 0,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    
    -- Coupon applied
    coupon_id INT NULL,
    coupon_code VARCHAR(50) NULL,
    
    -- Shipping address
    shipping_address JSON, -- Store complete address as JSON
    billing_address JSON,
    
    -- Tracking
    tracking_number VARCHAR(100),
    shipped_at TIMESTAMP NULL,
    delivered_at TIMESTAMP NULL,
    
    -- Notes
    order_notes TEXT,
    admin_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (supplier_id) REFERENCES users(id),
    FOREIGN KEY (coupon_id) REFERENCES coupons(id),
    INDEX idx_order_number (order_number),
    INDEX idx_user_id (user_id),
    INDEX idx_supplier_id (supplier_id),
    INDEX idx_status (status)
);

CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    product_id INT,
    variant_id INT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    product_name VARCHAR(200), -- Store product name at time of order
    product_sku VARCHAR(100),
    supplier_id INT, -- Denormalized for easier queries
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (variant_id) REFERENCES product_variants(id),
    FOREIGN KEY (supplier_id) REFERENCES users(id)
);

-- Order status history/tracking
CREATE TABLE order_tracking (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    status VARCHAR(100) NOT NULL,
    message TEXT,
    updated_by INT, -- Admin or Supplier who made the update
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- ================================
-- REVIEWS & RATINGS
-- ================================

CREATE TABLE product_reviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    user_id INT,
    order_id INT, -- Link to actual purchase for verified reviews
    rating INT CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(200),
    comment TEXT,
    is_verified BOOLEAN DEFAULT FALSE, -- Verified purchase
    is_approved BOOLEAN DEFAULT TRUE,
    helpful_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    UNIQUE KEY unique_user_product_review (user_id, product_id, order_id)
);

-- Users can mark reviews as helpful
CREATE TABLE review_helpfulness (
    id INT PRIMARY KEY AUTO_INCREMENT,
    review_id INT,
    user_id INT,
    is_helpful BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES product_reviews(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_review_vote (user_id, review_id)
);

-- ================================
-- COMMUNICATION & SUPPORT
-- ================================

CREATE TABLE contact_messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    subject VARCHAR(200),
    message TEXT NOT NULL,
    user_id INT NULL, -- If logged in user
    status ENUM('new', 'in_progress', 'resolved', 'closed') DEFAULT 'new',
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    assigned_to INT NULL, -- Admin user handling this
    admin_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);

-- Internal messaging between users (supplier-customer, customer-admin)
CREATE TABLE messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT,
    recipient_id INT,
    subject VARCHAR(200),
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    message_type ENUM('general', 'order_inquiry', 'product_inquiry', 'support') DEFAULT 'general',
    related_order_id INT NULL,
    related_product_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (recipient_id) REFERENCES users(id),
    FOREIGN KEY (related_order_id) REFERENCES orders(id),
    FOREIGN KEY (related_product_id) REFERENCES products(id)
);

-- ================================
-- ANALYTICS & REPORTING
-- ================================

CREATE TABLE page_views (
    id INT PRIMARY KEY AUTO_INCREMENT,
    page_type ENUM('product', 'category', 'home', 'search') NOT NULL,
    page_id INT NULL, -- Product ID, Category ID, etc.
    user_id INT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    referer VARCHAR(500),
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE search_queries (
    id INT PRIMARY KEY AUTO_INCREMENT,
    query VARCHAR(255) NOT NULL,
    user_id INT NULL,
    results_count INT DEFAULT 0,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ================================
-- NOTIFICATIONS
-- ================================

CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type ENUM('order', 'product', 'payment', 'system', 'promotion') NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(500), -- URL to redirect when clicked
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ================================
-- SYSTEM CONFIGURATION
-- ================================

CREATE TABLE site_settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type ENUM('string', 'integer', 'decimal', 'boolean', 'json') DEFAULT 'string',
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE, -- Can be accessed from frontend
    updated_by INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- ================================
-- AUDIT TRAIL
-- ================================

CREATE TABLE audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100) NOT NULL, -- login, logout, create_product, update_order, etc.
    table_name VARCHAR(100),
    record_id INT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ================================
-- INDEXES FOR PERFORMANCE
-- ================================

-- Additional indexes for common queries
CREATE INDEX idx_products_supplier_active ON products(supplier_id, is_active);
CREATE INDEX idx_products_category_active ON products(category_id, is_active);
CREATE INDEX idx_products_featured ON products(is_featured, is_active);
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
CREATE INDEX idx_orders_supplier_status ON orders(supplier_id, status);
CREATE INDEX idx_reviews_product_approved ON product_reviews(product_id, is_approved);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);

-- ================================
-- INITIAL DATA INSERTS
-- ================================

-- Insert default roles
INSERT INTO roles (name, description) VALUES 
('admin', 'Platform Administrator'),
('supplier', 'Product Supplier/Vendor'),
('consumer', 'Customer/Buyer');

-- Insert default admin user (password: Admin@123 - should be hashed in application)
INSERT INTO users (name, email, password_hash, role_id, is_verified) VALUES 
('System Admin', 'admin@mediplant.com', '$2b$12$example_hash_here', 1, TRUE);

-- Insert sample categories
INSERT INTO categories (name, slug, description) VALUES 
('Medicinal Herbs', 'medicinal-herbs', 'Traditional medicinal plants and herbs'),
('Ayurvedic Plants', 'ayurvedic-plants', 'Plants used in Ayurvedic medicine'),
('Aromatic Plants', 'aromatic-plants', 'Fragrant and aromatic medicinal plants'),
('Seeds & Saplings', 'seeds-saplings', 'Plant seeds and young saplings'),
('Dried Herbs', 'dried-herbs', 'Processed and dried medicinal herbs'),
('Essential Oils', 'essential-oils', 'Extracted essential oils from plants');

-- Insert sample site settings
INSERT INTO site_settings (setting_key, setting_value, setting_type, description, is_public) VALUES 
('site_name', 'MediPlant', 'string', 'Website name', TRUE),
('site_description', 'Medicinal Plant E-Commerce Platform', 'string', 'Website description', TRUE),
('default_currency', 'INR', 'string', 'Default currency code', TRUE),
('tax_rate', '18.0', 'decimal', 'Default tax rate percentage', FALSE),
('free_shipping_threshold', '500.0', 'decimal', 'Minimum order for free shipping', TRUE),
('max_cart_items', '50', 'integer', 'Maximum items in cart', TRUE);