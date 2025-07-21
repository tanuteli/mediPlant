# 🌿 MediPlant - Medicinal Plant E-Commerce Platform

Welcome to **MediPlant**, a comprehensive multi-vendor e-commerce platform for medicinal plants and herbal wellness products. Built with **Python (Flask)** and **MySQL**, this platform serves as a marketplace connecting suppliers, consumers, and administrators in the medicinal plant industry.

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
