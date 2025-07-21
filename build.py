#!/usr/bin/env python3
"""
MediPlant Build Script
Prepares the application for deployment
"""

import os
import sys
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

def print_header():
    """Print build header"""
    print("=" * 60)
    print("🏗️  MediPlant - Build Script")
    print("=" * 60)
    print()

def clean_build_directory():
    """Clean previous build artifacts"""
    print("🧹 Cleaning build directory...")
    
    build_dir = "build"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print("✅ Removed existing build directory")
    
    os.makedirs(build_dir, exist_ok=True)
    print("✅ Created fresh build directory")
    print()

def copy_source_files():
    """Copy source files to build directory"""
    print("📂 Copying source files...")
    
    # Files and directories to include
    include_items = [
        "app",
        "config.py", 
        "run.py",
        "requirements.txt",
        "README.md",
        "INSTALL.md",
        ".env.example"
    ]
    
    # Files and directories to exclude
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".git",
        "venv",
        "*.db",
        "logs",
        "backups",
        ".env"
    ]
    
    for item in include_items:
        if os.path.exists(item):
            dest = os.path.join("build", item)
            if os.path.isdir(item):
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*exclude_patterns))
            else:
                shutil.copy2(item, dest)
            print(f"✅ Copied: {item}")
        else:
            print(f"⚠️  Not found: {item}")
    
    print()

def create_production_config():
    """Create production configuration files"""
    print("⚙️  Creating production configuration...")
    
    # Create production .env file
    prod_env = """# MediPlant Production Configuration

# Database (Update with your production database)
DATABASE_URL=mysql+pymysql://username:password@localhost/mediplant_production

# Security (IMPORTANT: Change these values!)
SECRET_KEY=CHANGE-THIS-TO-A-SECURE-RANDOM-KEY
WTF_CSRF_SECRET_KEY=CHANGE-THIS-TO-A-SECURE-RANDOM-KEY

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Security Settings
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
PERMANENT_SESSION_LIFETIME=3600

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-production-email@gmail.com
MAIL_PASSWORD=your-production-app-password

# Payment Gateways
RAZORPAY_KEY_ID=your-production-razorpay-key
RAZORPAY_KEY_SECRET=your-production-razorpay-secret
PAYPAL_CLIENT_ID=your-production-paypal-id
PAYPAL_CLIENT_SECRET=your-production-paypal-secret

# File Upload
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,webp

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/mediplant.log
"""
    
    with open("build/.env.production", "w") as f:
        f.write(prod_env)
    print("✅ Created production environment template")
    
    # Create Dockerfile
    dockerfile = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    default-libmysqlclient-dev \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p app/static/uploads logs backups

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
"""
    
    with open("build/Dockerfile", "w") as f:
        f.write(dockerfile)
    print("✅ Created Dockerfile")
    
    # Create docker-compose.yml
    docker_compose = """version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=mysql+pymysql://mediplant:password@db:3306/mediplant_db
    depends_on:
      - db
    volumes:
      - ./app/static/uploads:/app/app/static/uploads
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: mediplant_db
      MYSQL_USER: mediplant
      MYSQL_PASSWORD: password
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  mysql_data:
"""
    
    with open("build/docker-compose.yml", "w") as f:
        f.write(docker_compose)
    print("✅ Created docker-compose.yml")
    
    # Create nginx configuration
    nginx_conf = """events {
    worker_connections 1024;
}

http {
    upstream mediplant {
        server web:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        
        # Static files
        location /static/ {
            alias /app/app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Proxy to Flask app
        location / {
            proxy_pass http://mediplant;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
"""
    
    with open("build/nginx.conf", "w") as f:
        f.write(nginx_conf)
    print("✅ Created nginx configuration")
    print()

def create_deployment_scripts():
    """Create deployment scripts for different platforms"""
    print("🚀 Creating deployment scripts...")
    
    # Heroku Procfile
    with open("build/Procfile", "w") as f:
        f.write("web: gunicorn run:app\n")
    print("✅ Created Procfile for Heroku")
    
    # PythonAnywhere WSGI file
    wsgi_content = """import sys
import os

# Add project directory to path
project_home = '/home/yourusername/mediplant'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from run import app as application

if __name__ == "__main__":
    application.run()
"""
    
    with open("build/wsgi.py", "w") as f:
        f.write(wsgi_content)
    print("✅ Created WSGI file for PythonAnywhere")
    
    # Render build script
    render_build = """#!/bin/bash
# Build script for Render.com

set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p app/static/uploads
mkdir -p logs

# Run database migrations (if applicable)
# python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

echo "Build completed successfully!"
"""
    
    with open("build/build.sh", "w") as f:
        f.write(render_build)
    os.chmod("build/build.sh", 0o755)
    print("✅ Created build script for Render")
    
    # Create deployment guide
    deploy_guide = """# 🚀 MediPlant Deployment Guide

## 📋 Pre-deployment Checklist

- [ ] Update `.env.production` with your actual values
- [ ] Set up production database (MySQL recommended)
- [ ] Configure email SMTP settings
- [ ] Set up payment gateway credentials
- [ ] Generate secure SECRET_KEY values
- [ ] Set up SSL certificates
- [ ] Configure domain and DNS

## 🐳 Docker Deployment

```bash
# 1. Copy files to your server
scp -r build/* user@your-server:/path/to/mediplant/

# 2. Navigate to project directory
cd /path/to/mediplant/

# 3. Copy production environment
cp .env.production .env

# 4. Build and start containers
docker-compose up -d

# 5. Create database tables
docker-compose exec web python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

## 🌐 Heroku Deployment

```bash
# 1. Install Heroku CLI and login
heroku login

# 2. Create new app
heroku create your-app-name

# 3. Add MySQL addon
heroku addons:create cleardb:ignite

# 4. Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production

# 5. Deploy
git push heroku main

# 6. Initialize database
heroku run python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

## 🐍 PythonAnywhere Deployment

1. Upload files to PythonAnywhere
2. Create virtual environment in Bash console
3. Install requirements: `pip install -r requirements.txt`
4. Configure WSGI file with provided template
5. Set up scheduled tasks for maintenance

## ☁️ Render.com Deployment

1. Connect GitHub repository to Render
2. Set environment variables in dashboard
3. Use provided build script: `./build.sh`
4. Set start command: `gunicorn run:app`

## 🔧 Post-deployment Tasks

1. **Database Setup:**
   ```bash
   # Create tables
   python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
   
   # Create admin user
   python create_admin.py
   ```

2. **SSL Configuration:**
   - Install SSL certificates
   - Configure nginx/Apache for HTTPS
   - Update security headers

3. **Monitoring Setup:**
   - Configure application logging
   - Set up error tracking (Sentry)
   - Monitor performance metrics

4. **Backup Strategy:**
   - Database backups
   - File upload backups
   - Configuration backups

## 🔒 Security Considerations

- Use environment variables for sensitive data
- Enable HTTPS/SSL everywhere
- Set up proper firewall rules
- Regular security updates
- Monitor for suspicious activity
- Implement rate limiting
- Use secure session configuration

## 📊 Performance Optimization

- Enable gzip compression
- Configure static file caching
- Use CDN for static assets
- Optimize database queries
- Implement Redis caching
- Monitor resource usage

---

For detailed configuration options, see the main README.md file.
"""
    
    with open("build/DEPLOYMENT.md", "w") as f:
        f.write(deploy_guide)
    print("✅ Created deployment guide")
    print()

def optimize_for_production():
    """Optimize files for production"""
    print("⚡ Optimizing for production...")
    
    # Create optimized requirements for production
    prod_requirements = """# Production Requirements for MediPlant

# Core Flask Framework
Flask==2.3.3
Werkzeug==2.3.7

# Database
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.23
PyMySQL==1.1.0

# Authentication & Security
Flask-Login==0.6.3
Flask-WTF==1.2.1
WTForms==3.1.0
bcrypt==4.0.1

# Email
Flask-Mail==0.9.1

# Environment & Configuration
python-dotenv==1.0.0

# Image Processing
Pillow==10.1.0

# Date/Time Utilities
python-dateutil==2.8.2

# HTTP Requests
requests==2.31.0

# Validation
email-validator==2.1.0

# Production Server
gunicorn==21.2.0

# Data Serialization
marshmallow==3.20.1

# Redis for Caching
redis==5.0.1
Flask-Caching==2.1.0

# Rate Limiting
Flask-Limiter==3.5.0

# CORS
Flask-CORS==4.0.0

# Timezone Support
pytz==2023.3

# Logging
colorlog==6.8.0
"""
    
    with open("build/requirements-prod.txt", "w") as f:
        f.write(prod_requirements)
    print("✅ Created optimized production requirements")
    
    print()

def create_build_archive():
    """Create deployment archive"""
    print("📦 Creating deployment archive...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"mediplant_build_{timestamp}.zip"
    
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("build"):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, "build")
                zipf.write(file_path, arc_path)
    
    file_size = os.path.getsize(archive_name) / (1024 * 1024)  # MB
    print(f"✅ Created deployment archive: {archive_name} ({file_size:.1f} MB)")
    print()

def print_build_summary():
    """Print build summary"""
    print("🎉 Build completed successfully!")
    print()
    print("📂 Build Contents:")
    print("   ├── app/                   # Application source code")
    print("   ├── config.py             # Configuration file")
    print("   ├── run.py                # Application entry point")
    print("   ├── requirements.txt      # Development dependencies")
    print("   ├── requirements-prod.txt # Production dependencies")
    print("   ├── .env.production       # Production environment template")
    print("   ├── Dockerfile            # Docker container configuration")
    print("   ├── docker-compose.yml    # Multi-container setup")
    print("   ├── nginx.conf            # Nginx configuration")
    print("   ├── Procfile              # Heroku process file")
    print("   ├── wsgi.py               # WSGI configuration")
    print("   ├── build.sh              # Render build script")
    print("   └── DEPLOYMENT.md         # Deployment instructions")
    print()
    print("📋 Next Steps:")
    print("1. Review and update .env.production with your settings")
    print("2. Choose your deployment platform (Docker, Heroku, etc.)")
    print("3. Follow the DEPLOYMENT.md guide for your platform")
    print("4. Test thoroughly in staging before production deployment")
    print()

def main():
    """Main build function"""
    print_header()
    
    try:
        clean_build_directory()
        copy_source_files()
        create_production_config()
        create_deployment_scripts()
        optimize_for_production()
        create_build_archive()
        print_build_summary()
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
