# 🌿 MediPlant - Medicinal Plant E-Commerce Platform

Welcome to *MediPlant*, a full-featured online store for exploring and purchasing medicinal plants and herbal wellness products.  
Built using *Python (Flask)* and *MySQL*, the platform combines educational value and e-commerce to promote natural remedies and plant-based health.

---

## 📌 Objectives

- Make traditional medicinal plants accessible online
- Educate users about plant benefits and uses
- Provide a smooth and secure shopping experience

---

## 🔑 Key Features

- 🪴 *Product Catalog*: List of medicinal plants with images, price, and usage info
- 🔍 *Search & Filters*: Browse by name, category, or benefit
- 📖 *Detailed Plant Pages*: Description, health benefits, and care instructions
- 🛒 *Cart & Checkout*: Add products and complete secure purchases
- 📦 *Order Tracking*: View current status of user orders
- 🌟 *Reviews & Ratings*: Customer feedback for each product
- 📧 *Contact Form*: Users can send inquiries or requests
- 🧙‍♂ *Admin Panel*: Manage products, orders, users, and messages

---

## ⚙ Tech Stack

| Layer       | Technology                   |
|-------------|------------------------------|
| Frontend    | HTML, CSS, Bootstrap, JS     |
| Backend     | Python (Flask)               |
| Database    | MySQL                        |
| Hosting     | PythonAnywhere / Render      |
| Payments    | Razorpay / PayPal            |

---

## 📂 Folder Structure

```
mediplant/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── user.py
│   │   ├── admin.py
│   │   ├── product.py
│   │   └── order.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── product_detail.html
│   │   ├── cart.html
│   │   ├── checkout.html
│   │   ├── contact.html
│   │   └── admin/
│   │       ├── dashboard.html
│   │       ├── add_product.html
│   │       ├── manage_orders.html
│   │       └── view_messages.html
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── config.py
├── run.py
├── requirements.txt
└── README.md
```


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
```

### 4. Initialize Tables
```bash
flask db init
flask db migrate
flask db upgrade
```

### 5. Run the Server
```bash
python run.py
```
Open your browser: http://localhost:5000

---

## 🔐 Admin Access
Login via `/admin/login`

**Default Admin:**
- Email: `admin@example.com`
- Password: `admin123`

---

## 🧪 Testing Checklist
- [ ] Register as a user
- [ ] Browse plant products
- [ ] Add items to cart
- [ ] Checkout & place order
- [ ] Admin: Add/Edit products
- [ ] Submit reviews, ratings
- [ ] Contact via form
- [ ] Track orders

---

## 📜 License
MIT License
