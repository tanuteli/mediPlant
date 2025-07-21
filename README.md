# 🌿 MediPlant - Medicinal Plant E-Commerce Platform

Welcome to **MediPlant**, a comprehensive multi-vendor e-commerce platform for medicinal plants and herbal wellness products. Built with **Python (Flask)** and **MySQL/SQLite**, this platform serves as a marketplace connecting suppliers, consumers, and administrators in the medicinal plant industry.

---

## 📌 Platform Overview

MediPlant is designed as a complete Amazon-like e-commerce solution with three distinct user roles:
- **👨‍💼 Admin**: Platform management and oversight
- **🌱 Suppliers**: Product vendors and sellers
- **🛒 Consumers**: Buyers and end users

The platform facilitates secure transactions, inventory management, and provides educational content about medicinal plants and their benefits.

---

## 🎯 Core Objectives

- Create a trusted marketplace for medicinal plants and herbal products
- Enable suppliers to reach a wider customer base through digital commerce
- Educate consumers about plant benefits, usage, and safety
- Provide a seamless, secure, and feature-rich shopping experience
- Support sustainable and traditional medicine practices

---

## ✨ Current Implementation Status

### ✅ **Completed Features**
- **Frontend Templates**: All major HTML templates created with modern, responsive design
- **User Interface**: Beautiful landing page with animations and interactive elements
- **Authentication System**: Login, registration, and role-based access control templates
- **Admin Dashboard**: Complete admin interface with user and supplier management
- **Supplier Dashboard**: Product management, orders, and analytics interfaces
- **Consumer Experience**: Product browsing, cart, wishlist, and checkout pages
- **Database Schema**: Complete 25+ table schema with relationships
- **CSS Framework**: Custom styling with Bootstrap 5 and themed color palette
- **JavaScript**: Interactive features, AJAX functionality, and animations
- **Blueprints**: Modular Flask application structure with organized routes

### 🚧 **In Progress**
- **Database Integration**: Models implementation and database initialization
- **Backend Routes**: API endpoints and business logic implementation
- **Payment Integration**: Razorpay/PayPal gateway setup
- **Image Upload**: Product and user image handling system
- **Email System**: SMTP configuration for notifications

### 📋 **Planned Features**
- **Search & Filtering**: Advanced product search with filters
- **Analytics Dashboard**: Sales and performance reporting
- **Review System**: Product ratings and reviews
- **Order Tracking**: Real-time order status updates
- **Inventory Management**: Stock level monitoring and alerts

---

## ⚙️ Tech Stack

| Layer       | Technology                   | Status |
|-------------|------------------------------|--------|
| Frontend    | HTML5, CSS3, Bootstrap 5, JS | ✅ Complete |
| Backend     | Python (Flask)               | 🚧 In Progress |
| Database    | MySQL / SQLite (dev)         | 🚧 In Progress |
| Hosting     | PythonAnywhere / Render      | 📋 Planned |
| Payments    | Razorpay / PayPal            | 📋 Planned |
| Auth        | Flask-Login, bcrypt          | 🚧 In Progress |
| File Upload | Flask-WTF, Pillow           | 📋 Planned |

---

## 🔑 Platform Features

### 👨‍💼 **Admin Features**
- **User Management**: Add, remove, suspend, and manage all platform users
- **Supplier Management**: Approve/reject supplier registrations and monitor activities
- **Sales Analytics**: Comprehensive dashboard with sales reports, revenue tracking
- **Order Oversight**: Monitor all platform transactions and order statuses
- **Content Management**: Manage product categories, featured products, and promotions
- **Message Center**: Handle customer inquiries and supplier communications
- **Platform Settings**: Configure payment methods, shipping options, and policies
- **Review Moderation**: Monitor and moderate product reviews and ratings

### 🌱 **Supplier Features**
- **Product Management**: Full CRUD operations (Create, Read, Update, Delete) for products
- **Inventory Control**: Manage stock levels, pricing, and product availability
- **Order Management**: View, process, and fulfill customer orders
- **Sales Dashboard**: Track earnings, order history, and performance metrics
- **Profile Management**: Update business information, contact details, and certifications
- **Bulk Upload**: Upload multiple products via CSV/Excel files
- **Promotion Tools**: Create discounts, deals, and promotional campaigns
- **Analytics**: View product performance and customer insights

### 🛒 **Consumer Features**
- **Product Browsing**: Advanced search and filtering by category, price, benefits
- **Shopping Cart**: Add/remove items, save for later, quantity management
- **Secure Checkout**: Multiple payment options and secure transaction processing
- **Order Tracking**: Real-time order status updates and delivery tracking
- **Reviews & Ratings**: Rate products and write detailed reviews
- **Wishlist**: Save favorite products for future purchases
- **Account Management**: Order history, address book, payment methods
- **Educational Content**: Access plant guides, usage instructions, and health benefits

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- MySQL server (optional - SQLite included for development)
- Git for version control

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/tanuteli/mediPlant.git
cd mediPlant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=sqlite:///mediplant.db
# For MySQL: DATABASE_URL=mysql+pymysql://username:password@localhost/mediplant_db

# Security
SECRET_KEY=your-super-secret-key-here
WTF_CSRF_SECRET_KEY=your-csrf-secret-key

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Payment Gateways (Optional)
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-secret

# Upload Configuration
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### 3. Database Setup
```bash
# Initialize database (creates tables)
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized!')"

# Optional: Create sample data
python create_sample_data.py
```

### 4. Run the Application
```bash
# Development server
python run.py

# The application will be available at:
# http://localhost:5000
```

---

## 📂 Project Structure

```
mediPlant/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models (25+ tables)
│   ├── database.py              # Database initialization
│   ├── config.py                # Configuration settings
│   ├── cli.py                   # Command line interface
│   │
│   ├── routes/                  # Blueprint routes
│   │   ├── __init__.py
│   │   ├── main.py              # Main routes (index, contact, about)
│   │   ├── auth.py              # Authentication routes
│   │   ├── admin.py             # Admin dashboard routes
│   │   ├── supplier.py          # Supplier dashboard routes
│   │   ├── consumer.py          # Consumer routes
│   │   ├── product.py           # Product management routes
│   │   ├── order.py             # Order processing routes
│   │   └── review.py            # Review system routes
│   │
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html            # Base template with navigation
│   │   ├── index.html           # Landing page with animations
│   │   ├── contact.html         # Contact and FAQ page
│   │   │
│   │   ├── auth/                # Authentication templates
│   │   │   ├── login.html       # Login form
│   │   │   └── register.html    # Registration with role selection
│   │   │
│   │   ├── admin/               # Admin dashboard templates
│   │   │   ├── dashboard.html   # Admin overview
│   │   │   ├── users.html       # User management
│   │   │   ├── suppliers.html   # Supplier approval
│   │   │   ├── products.html    # Product oversight
│   │   │   ├── orders.html      # Order monitoring
│   │   │   └── analytics.html   # Sales analytics
│   │   │
│   │   ├── supplier/            # Supplier dashboard templates
│   │   │   ├── dashboard.html   # Supplier overview
│   │   │   ├── products.html    # Product management
│   │   │   ├── orders.html      # Order fulfillment
│   │   │   └── inventory.html   # Stock management
│   │   │
│   │   └── consumer/            # Consumer interface templates
│   │       ├── products.html    # Product catalog
│   │       ├── product_detail.html # Product details
│   │       ├── cart.html        # Shopping cart
│   │       ├── wishlist.html    # Saved items
│   │       └── checkout.html    # Purchase process
│   │
│   └── static/                  # Static assets
│       ├── css/
│       │   ├── main.css         # Main stylesheet with theme
│       │   ├── admin.css        # Admin-specific styles
│       │   ├── supplier.css     # Supplier dashboard styles
│       │   └── consumer.css     # Consumer interface styles
│       ├── js/
│       │   ├── main.js          # Core JavaScript functionality
│       │   ├── admin.js         # Admin dashboard scripts
│       │   ├── supplier.js      # Supplier functionality
│       │   └── consumer.js      # Consumer interactions
│       └── images/              # Image assets
│           ├── hero/            # Landing page images
│           ├── products/        # Product images
│           └── users/           # User avatars
│
├── migrations/                  # Database migration files
├── tests/                       # Test suite
├── docs/                        # Documentation
│   ├── ER_Diagram.md           # Entity Relationship Diagram
│   └── schema.sql              # Database schema
│
├── .env                        # Environment variables (create this)
├── .gitignore                  # Git ignore rules
├── config.py                   # Configuration classes
├── run.py                      # Application entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🎨 Design & User Experience

### 🎨 **Visual Design System**
- **Color Palette**: 
  - Primary: `#212121` (Dark Gray)
  - Secondary: `#6D9886` (Forest Green)
  - Accent: `#D9CAB3` (Warm Beige)
  - Light: `#F6F6F6` (Off White)
- **Typography**: Modern sans-serif fonts with responsive sizing
- **Components**: Consistent card designs, buttons, and form elements
- **Animations**: Smooth transitions, scroll animations, and hover effects

### 📱 **Responsive Features**
- Mobile-first design approach
- Bootstrap 5 grid system
- Touch-friendly interface elements
- Optimized images and loading
- Progressive Web App ready

### 🎯 **User Experience Highlights**
- Intuitive navigation with breadcrumbs
- Quick search with live suggestions
- Interactive product cards with hover effects
- Smooth page transitions and animations
- Loading states and progress indicators
- Comprehensive error handling and validation

---

## 🗄️ Database Schema

### **Core Tables (25+ Tables)**
```sql
-- User Management
Users, UserProfiles, UserAddresses, UserSessions

-- Product Catalog
Products, Categories, SubCategories, ProductImages, ProductVariants

-- E-Commerce
Orders, OrderItems, Cart, CartItems, Wishlist, WishlistItems

-- Reviews & Ratings
Reviews, ReviewImages, ProductRatings

-- Supplier Management
SupplierProfiles, SupplierDocuments, SupplierBankDetails

-- Financial
Payments, PaymentMethods, Transactions, Invoices

-- Communication
Messages, Notifications, NewsletterSubscriptions

-- System
AuditLogs, SystemSettings, EmailTemplates
```

### **Key Relationships**
- One-to-Many: User → Orders, Supplier → Products
- Many-to-Many: Products ↔ Categories, Users ↔ Wishlist
- Polymorphic: Reviews (Users can review Products)

---

## 🔧 Configuration Guide

### **Database Configuration**
```python
# For Development (SQLite)
SQLALCHEMY_DATABASE_URI = 'sqlite:///mediplant.db'

# For Production (MySQL)
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:pass@localhost/mediplant_db'

# Additional Settings
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True  # For debugging
```

### **Security Configuration**
```python
# Essential Security Settings
SECRET_KEY = 'your-secret-key'
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = 3600

# Session Configuration
PERMANENT_SESSION_LIFETIME = timedelta(days=1)
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True
```

### **File Upload Configuration**
```python
# Upload Settings
UPLOAD_FOLDER = 'app/static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
```

---

## 🧪 Testing Guide

### **Frontend Testing**
```bash
# Test responsive design
# - Open browser developer tools
# - Test on mobile, tablet, desktop viewports
# - Verify touch interactions work properly

# Test JavaScript functionality
# - Cart add/remove operations
# - Wishlist management
# - Search and filtering
# - Form validations
```

### **Backend Testing**
```bash
# Run test suite (when implemented)
python -m pytest tests/

# Manual API testing
curl -X GET http://localhost:5000/api/products
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'
```

### **Database Testing**
```bash
# Test database connection
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print('DB connected:', db.engine.execute('SELECT 1').scalar())"

# Verify table creation
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Tables created successfully')"
```

---

## 🚀 Deployment Options

### **Option 1: Local Development**
```bash
# Clone and setup (as shown in Quick Start)
python run.py
# Access at http://localhost:5000
```

### **Option 2: PythonAnywhere**
1. Upload files to PythonAnywhere
2. Create virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.9 mediplant
   pip install -r requirements.txt
   ```
3. Configure WSGI file
4. Set environment variables in .env
5. Create MySQL database through console

### **Option 3: Render/Heroku**
1. Connect GitHub repository
2. Set environment variables:
   - `SECRET_KEY`
   - `DATABASE_URL`
   - `FLASK_ENV=production`
3. Configure build command: `pip install -r requirements.txt`
4. Configure start command: `python run.py`

---

## 🛡️ Security Features

### **Implemented Security**
- CSRF protection on all forms
- Password hashing with bcrypt
- Session management with Flask-Login
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)

### **Planned Security Enhancements**
- Rate limiting on API endpoints
- Two-factor authentication
- OAuth integration (Google, Facebook)
- File upload validation
- Security headers implementation
- Regular security audits

---

## 🐛 Troubleshooting

### **Common Issues**

**Database Connection Error**
```bash
# Check database URL in .env
# For SQLite: Ensure directory is writable
# For MySQL: Verify credentials and database exists
```

**Template Not Found**
```bash
# Verify template exists in correct directory
# Check blueprint registration in __init__.py
# Ensure template path is correct in route
```

**Static Files Not Loading**
```bash
# Check FLASK_ENV=development for auto-reload
# Verify static folder path
# Clear browser cache
```

**Import Errors**
```bash
# Ensure virtual environment is activated
# Check all dependencies installed: pip install -r requirements.txt
# Verify Python path and PYTHONPATH
```

---

## 📈 Performance Optimization

### **Frontend Optimization**
- Minified CSS and JavaScript
- Optimized images with WebP format
- Lazy loading for product images
- CDN integration for static assets
- Browser caching headers

### **Backend Optimization**
- Database query optimization
- Redis caching for session data
- Background task processing
- Connection pooling
- Database indexing

---

## 🤝 Contributing

### **Development Workflow**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Commit with descriptive messages
5. Push to branch: `git push origin feature/new-feature`
6. Create Pull Request

### **Code Standards**
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Write docstrings for functions and classes
- Include unit tests for new features
- Update documentation as needed

---

## 📞 Support & Documentation

### **Getting Help**
- 📧 Email: support@mediplant.com
- 📖 Documentation: `/docs` directory
- 🐛 Issues: GitHub Issues tab
- 💬 Discussions: GitHub Discussions

### **Additional Resources**
- Database Schema: `docs/ER_Diagram.md`
- API Documentation: `docs/api.md` (planned)
- Deployment Guide: `docs/deployment.md` (planned)
- User Manual: `docs/user_guide.md` (planned)

---

## 📜 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- Bootstrap team for the excellent CSS framework
- Flask community for the amazing web framework
- Contributors and testers
- Open source community

---

**Last Updated**: January 22, 2025  
**Version**: 1.0.0-beta  
**Maintainer**: MediPlant Development Team

### 👨‍💼 **Admin Features**
- **User Management**: Add, remove, suspend, and manage all platform users
- **Supplier Management**: Approve/reject supplier registrations and monitor activities
- **Sales Analytics**: Comprehensive dashboard with sales reports, revenue tracking
- **Order Oversight**: Monitor all platform transactions and order statuses
- **Content Management**: Manage product categories, featured products, and promotions
- **Message Center**: Handle customer inquiries and supplier communications
- **Platform Settings**: Configure payment methods, shipping options, and policies
- **Review Moderation**: Monitor and moderate product reviews and ratings

### 🌱 **Supplier Features**
- **Product Management**: Full CRUD operations (Create, Read, Update, Delete) for products
- **Inventory Control**: Manage stock levels, pricing, and product availability
- **Order Management**: View, process, and fulfill customer orders
- **Sales Dashboard**: Track earnings, order history, and performance metrics
- **Profile Management**: Update business information, contact details, and certifications
- **Bulk Upload**: Upload multiple products via CSV/Excel files
- **Promotion Tools**: Create discounts, deals, and promotional campaigns
- **Analytics**: View product performance and customer insights

### 🛒 **Consumer Features**
- **Product Browsing**: Advanced search and filtering by category, price, benefits
- **Shopping Cart**: Add/remove items, save for later, quantity management
- **Secure Checkout**: Multiple payment options and secure transaction processing
- **Order Tracking**: Real-time order status updates and delivery tracking
- **Reviews & Ratings**: Rate products and write detailed reviews
- **Wishlist**: Save favorite products for future purchases
- **Account Management**: Order history, address book, payment methods
- **Educational Content**: Access plant guides, usage instructions, and health benefits

---

## ⚙ Tech Stack

| Layer       | Technology                   |
|-------------|------------------------------|
| Frontend    | HTML, CSS, Bootstrap, JS     |
| Backend     | Python (Flask)               |
| Database    | MySQL                        |
| Hosting     | PythonAnywhere / Render      |
| Payments    | Razorpay / PayPal            |
| Auth        | Flask-Login, bcrypt          |
| File Upload | Flask-WTF, Pillow           |

---

## 🚀 Key Platform Capabilities

### 🔐 **Multi-Role Authentication System**
- Role-based access control (Admin, Supplier, Consumer)
- Secure registration and login with email verification
- Password encryption and session management
- Social media login integration (Google, Facebook)

### 💰 **Complete E-Commerce Functionality**
- Multi-vendor marketplace architecture
- Shopping cart and wishlist management
- Multiple payment gateway integration
- Order processing and fulfillment workflow
- Invoice generation and receipt management

### 📊 **Advanced Analytics & Reporting**
- Real-time sales and revenue tracking
- Product performance analytics
- Customer behavior insights
- Supplier performance metrics
- Admin dashboard with comprehensive reports

### 🔍 **Smart Search & Discovery**
- Advanced product search with filters
- Category-based browsing
- Price range and benefit-based filtering
- Recommendation engine for related products
- Featured and trending product sections

### 📱 **Responsive & User-Friendly Design**
- Mobile-responsive interface
- Intuitive navigation and user experience
- Quick product preview and comparison
- Easy checkout process
- Accessible design following web standards

---

## 📂 Folder Structure

```
mediplant/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── supplier.py
│   │   ├── consumer.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── review.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── contact.html
│   │   └── admin/
│   │       ├── dashboard.html
│   │       ├── users.html
│   │       ├── suppliers.html
│   │       ├── products.html
│   │       ├── orders.html
│   │       ├── analytics.html
│   │       └── messages.html
│   │   └── supplier/
│   │       ├── dashboard.html
│   │       ├── add_product.html
│   │       ├── my_products.html
│   │       ├── edit_product.html
│   │       ├── orders.html
│   │       ├── analytics.html
│   │       └── profile.html
│   │   └── consumer/
│   │       ├── home.html
│   │       ├── products.html
│   │       ├── product_detail.html
│   │       ├── cart.html
│   │       ├── checkout.html
│   │       ├── orders.html
│   │       ├── wishlist.html
│   │       └── profile.html
│   └── static/
│       ├── css/
│       │   ├── admin.css
│       │   ├── supplier.css
│       │   ├── consumer.css
│       │   └── main.css
│       ├── js/
│       │   ├── admin.js
│       │   ├── supplier.js
│       │   ├── consumer.js
│       │   └── main.js
│       └── images/
│           ├── products/
│           ├── users/
│           └── assets/
├── migrations/
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

---

## 🎨 User Interface & Experience

### 📱 **Responsive Design**
- Mobile-first approach with Bootstrap framework
- Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- Touch-friendly interface for mobile devices
- Progressive Web App (PWA) capabilities

### 🎯 **User Experience Features**
- Intuitive navigation with breadcrumbs
- Quick search with autocomplete suggestions
- Product comparison functionality
- One-click reorder for repeat purchases
- Guest checkout option
- Real-time notifications and alerts

### 🎨 **Visual Design**
- Clean, modern interface with plant-themed aesthetics
- High-quality product image galleries with zoom functionality
- Interactive product filters and sorting options
- Color-coded order status indicators
- Dashboard widgets with data visualizations


---

## 🛠 Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/yourusername/mediplant.git
cd mediplant
```

### 2. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure MySQL
Create a database: `mediplant_db`

Set your DB credentials in `config.py`:

```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://username:password@localhost/mediplant_db"
SECRET_KEY = "your-secret-key-here"
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = "your-email@gmail.com"
MAIL_PASSWORD = "your-app-password"
```

### 4. Environment Variables
Create a `.env` file for sensitive configurations:

```bash
SECRET_KEY=your-super-secret-key
DATABASE_URL=mysql+pymysql://username:password@localhost/mediplant_db
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
```

### 5. Initialize Database Tables
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Seed Initial Data (Optional)
```bash
python seed_data.py  # Creates admin user and sample categories
```

### 7. Run the Server
```bash
python run.py
```
Open your browser: http://localhost:5000

---

## 🔐 Default Access Credentials

### Admin Access
- **URL**: `/admin/login`
- **Email**: `admin@mediplant.com`
- **Password**: `Admin@123`

### Supplier Demo Account
- **URL**: `/supplier/login`
- **Email**: `supplier@mediplant.com`
- **Password**: `Supplier@123`

### Consumer Demo Account
- **URL**: `/login`
- **Email**: `consumer@mediplant.com`
- **Password**: `Consumer@123`

---

## 🚀 Deployment Options

### Option 1: PythonAnywhere
1. Upload project files to PythonAnywhere
2. Create virtual environment and install requirements
3. Configure WSGI file to point to your Flask app
4. Set up MySQL database through console

### Option 2: Render.com
1. Connect GitHub repository to Render
2. Set environment variables in dashboard
3. Configure build and start commands
4. Deploy with automatic SSL certificate

### Option 3: Heroku
1. Install Heroku CLI and login
2. Create new Heroku app
3. Add ClearDB MySQL addon
4. Configure environment variables
5. Deploy using Git

---

## 🧪 Complete Testing Checklist

### Admin Testing
- [ ] Login to admin dashboard
- [ ] Add/edit/delete users
- [ ] Approve/reject supplier applications
- [ ] View sales analytics and reports
- [ ] Manage product categories
- [ ] Monitor orders and transactions
- [ ] Handle customer support messages
- [ ] Moderate product reviews

### Supplier Testing
- [ ] Register as supplier and get approved
- [ ] Add new products with images
- [ ] Edit product details and pricing
- [ ] Manage inventory levels
- [ ] Process incoming orders
- [ ] Update order status
- [ ] View sales performance
- [ ] Bulk upload products via CSV

### Consumer Testing
- [ ] Register new account with email verification
- [ ] Browse products by category
- [ ] Use search and filter functionality
- [ ] Add products to cart and wishlist
- [ ] Apply coupon codes and discounts
- [ ] Complete checkout with payment
- [ ] Track order status
- [ ] Write product reviews and ratings
- [ ] Update profile and addresses

### General Testing
- [ ] Mobile responsiveness across devices
- [ ] Cross-browser compatibility
- [ ] Email notifications working
- [ ] Payment gateway integration
- [ ] Security measures (SQL injection, XSS)
- [ ] Performance under load
- [ ] Backup and recovery procedures

---

## 📊 Database Schema Overview

### Core Tables
- **Users**: Admin, Supplier, Consumer accounts
- **Products**: Product catalog with categories
- **Orders**: Purchase transactions and items
- **Cart**: Shopping cart management
- **Reviews**: Product ratings and feedback
- **Categories**: Product categorization
- **Addresses**: User shipping addresses
- **Payments**: Transaction records
- **Messages**: Customer support tickets

---

## 🔧 Configuration Guide

### Email Setup
Configure SMTP settings for email notifications:
- User registration confirmation
- Order status updates
- Password reset emails
- Admin notifications

### Payment Gateway
Integrate multiple payment options:
- Razorpay for Indian market
- PayPal for international transactions
- Stripe for credit card processing
- Cash on Delivery option

### Security Features
- Password hashing with bcrypt
- CSRF protection on forms
- SQL injection prevention
- XSS protection
- Session management
- Rate limiting on API endpoints

---

## 📈 Analytics & Reporting

### Admin Analytics
- Total revenue and profit margins
- User registration trends
- Top-selling products
- Supplier performance metrics
- Geographic sales distribution

### Supplier Analytics
- Individual sales performance
- Product view and conversion rates
- Customer demographics
- Seasonal trends
- Inventory turnover rates

### Consumer Insights
- Purchase history analysis
- Wishlist trends
- Review sentiment analysis
- Repeat purchase patterns
- Abandoned cart recovery

---

## 🛡️ Security Measures

- **Data Encryption**: All sensitive data encrypted at rest
- **Secure Communications**: HTTPS/SSL implementation
- **Input Validation**: Server-side validation for all forms
- **Authentication**: Multi-factor authentication option
- **Authorization**: Role-based access controls
- **Audit Logging**: Comprehensive activity tracking
- **Regular Backups**: Automated database backups
- **Vulnerability Scanning**: Regular security assessments

---

## 🔄 API Endpoints

### Authentication APIs
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/reset-password` - Password reset

### Product APIs
- `GET /api/products` - List all products
- `GET /api/products/{id}` - Get product details
- `POST /api/products` - Create product (Supplier)
- `PUT /api/products/{id}` - Update product (Supplier)
- `DELETE /api/products/{id}` - Delete product (Supplier)

### Order APIs
- `GET /api/orders` - User's orders
- `POST /api/orders` - Create new order
- `PUT /api/orders/{id}/status` - Update order status
- `GET /api/orders/{id}/track` - Track order

### Cart APIs
- `GET /api/cart` - Get cart items
- `POST /api/cart/add` - Add item to cart
- `PUT /api/cart/update` - Update cart quantity
- `DELETE /api/cart/remove` - Remove from cart

---

## 📜 License
MIT License
