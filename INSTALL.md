# 🚀 MediPlant Quick Installation Guide

This guide will get you up and running with MediPlant in under 10 minutes!

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **MySQL** (optional - SQLite included for development)

## ⚡ Quick Setup (Automated)

### Option 1: Using Setup Script (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/tanuteli/mediPlant.git
cd mediPlant

# 2. Run the automated setup script
python setup.py

# 3. Follow the on-screen instructions
```

The setup script will automatically:
- ✅ Check Python version compatibility
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create environment configuration
- ✅ Set up database structure
- ✅ Create necessary directories
- ✅ Generate sample data script

### Option 2: Manual Setup

```bash
# 1. Clone and navigate
git clone https://github.com/tanuteli/mediPlant.git
cd mediPlant

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create environment file
cp .env.example .env  # Edit with your settings

# 6. Initialize database
python create_sample_data.py

# 7. Run the application
python run.py
```

## 🔧 Configuration

### Database Configuration

**For Development (Default - SQLite):**
```env
DATABASE_URL=sqlite:///mediplant.db
```

**For Production (MySQL):**
```env
DATABASE_URL=mysql+pymysql://username:password@localhost/mediplant_db
```

### Security Configuration

```env
SECRET_KEY=your-super-secret-key-here
WTF_CSRF_SECRET_KEY=your-csrf-secret-key
```

### Email Configuration (Optional)

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 🚀 Running the Application

```bash
# Activate virtual environment (if not already active)
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Start the development server
python run.py

# Application will be available at:
# http://localhost:5000
```

## 👤 Default Login Credentials

After running the sample data script:

### Admin Access
- **URL**: http://localhost:5000/admin/login
- **Email**: admin@mediplant.com
- **Password**: Admin@123

### Supplier Access  
- **URL**: http://localhost:5000/login
- **Email**: supplier@mediplant.com
- **Password**: Supplier@123

### Consumer Access
- **URL**: http://localhost:5000/login  
- **Email**: consumer@mediplant.com
- **Password**: Consumer@123

## 📁 Key Files & Directories

```
mediPlant/
├── app/                    # Main application package
├── requirements.txt        # Python dependencies
├── run.py                 # Application entry point
├── .env                   # Environment configuration
├── setup.py              # Automated setup script
└── create_sample_data.py  # Sample data generator
```

## 🧪 Testing Your Installation

1. **Test Database Connection:**
   ```bash
   python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print('✅ Database connected!')"
   ```

2. **Test Web Interface:**
   - Visit http://localhost:5000
   - Should see the MediPlant landing page

3. **Test Login System:**
   - Try logging in with the default credentials
   - Navigate through different user dashboards

## 🆘 Common Issues & Solutions

### Issue: "ModuleNotFoundError"
**Solution:** Make sure virtual environment is activated and dependencies are installed
```bash
# Activate venv and reinstall
pip install -r requirements.txt
```

### Issue: "Database connection failed"
**Solution:** Check your DATABASE_URL in .env file
```bash
# For SQLite (default)
DATABASE_URL=sqlite:///mediplant.db

# Make sure the directory is writable
```

### Issue: "Template not found"
**Solution:** Verify you're in the correct directory and all files are present
```bash
# Check if you're in the project root
ls -la app/templates/
```

### Issue: "Port 5000 already in use"
**Solution:** Either kill the process using port 5000 or change the port
```bash
# Change port in run.py or set environment variable
export PORT=5001
python run.py
```

## 🔄 Development Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Make your changes

# 3. Test changes
python run.py

# 4. Create new migrations (if database changes)
flask db migrate -m "Description of changes"
flask db upgrade
```

## 📚 Next Steps

1. **Customize Configuration:** Edit `.env` file with your specific settings
2. **Add Real Data:** Replace sample data with actual products
3. **Configure Payments:** Set up Razorpay/PayPal credentials
4. **Deploy:** Follow deployment guide in README.md
5. **Secure:** Update security settings for production

## 📞 Getting Help

- 📖 **Full Documentation:** README.md
- 🐛 **Report Issues:** GitHub Issues tab
- 💬 **Discussions:** GitHub Discussions
- 📧 **Email Support:** support@mediplant.com

---

**Happy coding! 🌿✨**
