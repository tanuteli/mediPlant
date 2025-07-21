# Helper Utilities for MediPlant

import os
import uuid
from datetime import datetime
from PIL import Image
import secrets
from werkzeug.utils import secure_filename
from flask import current_app, url_for
import re

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def generate_unique_filename(filename):
    """Generate unique filename while preserving extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    unique_name = str(uuid.uuid4().hex)
    return f"{unique_name}.{ext}" if ext else unique_name

def save_uploaded_file(file, folder='products'):
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        # Generate secure filename
        original_filename = secure_filename(file.filename)
        filename = generate_unique_filename(original_filename)
        
        # Create folder path
        folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(folder_path, filename)
        file.save(file_path)
        
        # Optimize image if it's an image file
        if folder in ['products', 'users'] and filename.split('.')[-1].lower() in ['jpg', 'jpeg', 'png']:
            optimize_image(file_path)
        
        return filename
    return None

def optimize_image(file_path, max_size=(800, 800), quality=85):
    """Optimize image for web usage"""
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(file_path, 'JPEG', quality=quality, optimize=True)
    except Exception as e:
        current_app.logger.error(f"Image optimization failed: {str(e)}")

def generate_sku():
    """Generate unique SKU for products"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_part = secrets.token_hex(4).upper()
    return f"MP{timestamp}{random_part}"

def format_currency(amount, currency='INR'):
    """Format currency amount"""
    if currency == 'INR':
        return f"₹{amount:,.2f}"
    elif currency == 'USD':
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def calculate_tax(amount, tax_rate=0.18):
    """Calculate tax amount (default 18% GST for India)"""
    return round(amount * tax_rate, 2)

def calculate_shipping(amount, weight=0, distance=0):
    """Calculate shipping cost"""
    # Free shipping for orders above ₹500
    if amount >= 500:
        return 0.0
    
    # Base shipping cost
    base_cost = 50.0
    
    # Weight-based calculation (₹10 per kg)
    weight_cost = weight * 10.0
    
    # Distance-based calculation (₹2 per km for long distances)
    distance_cost = max(0, (distance - 50) * 2.0) if distance > 50 else 0
    
    return round(base_cost + weight_cost + distance_cost, 2)

def generate_order_number():
    """Generate unique order number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = secrets.token_hex(3).upper()
    return f"ORD{timestamp}{random_part}"

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate Indian phone number format"""
    # Remove all non-digit characters
    phone_digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid Indian mobile number
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone_digits) is not None

def sanitize_search_query(query):
    """Sanitize search query for safety"""
    if not query:
        return ''
    
    # Remove special characters except space, hyphen, and underscore
    sanitized = re.sub(r'[^\w\s\-_]', '', query)
    
    # Limit length
    return sanitized[:100].strip()

def generate_slug(text):
    """Generate URL-friendly slug from text"""
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def time_ago(dt):
    """Return human-readable time difference"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

def calculate_discount_percentage(original_price, sale_price):
    """Calculate discount percentage"""
    if original_price <= 0:
        return 0
    
    discount = ((original_price - sale_price) / original_price) * 100
    return round(max(0, discount), 1)

def get_image_url(filename, folder='products'):
    """Get URL for uploaded image"""
    if filename:
        return url_for('static', filename=f'uploads/{folder}/{filename}')
    else:
        return url_for('static', filename=f'images/default/{folder}_default.jpg')

def truncate_text(text, length=100, suffix='...'):
    """Truncate text to specified length"""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + suffix

def generate_verification_token():
    """Generate secure verification token"""
    return secrets.token_urlsafe(32)

def is_safe_url(target):
    """Check if URL is safe for redirects"""
    from urllib.parse import urlparse, urljoin
    from flask import request
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_client_ip():
    """Get client IP address"""
    from flask import request
    
    # Check for X-Forwarded-For header (proxy/load balancer)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    
    # Check for X-Real-IP header
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    
    # Default to remote address
    return request.remote_addr

def create_thumbnail(image_path, size=(150, 150)):
    """Create thumbnail from image"""
    try:
        with Image.open(image_path) as img:
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Generate thumbnail filename
            filename, ext = os.path.splitext(image_path)
            thumbnail_path = f"{filename}_thumb{ext}"
            
            # Save thumbnail
            img.save(thumbnail_path, quality=90, optimize=True)
            
            return os.path.basename(thumbnail_path)
    except Exception as e:
        current_app.logger.error(f"Thumbnail creation failed: {str(e)}")
        return None
