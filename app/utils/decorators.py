# Custom Decorators for MediPlant

from functools import wraps
from flask import abort, flash, redirect, url_for, request, jsonify
from flask_login import current_user
import time
from collections import defaultdict

# Rate limiting storage (in production, use Redis)
request_counts = defaultdict(list)

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.role or current_user.role.name != 'admin':
            abort(403)  # Forbidden
        
        return f(*args, **kwargs)
    return decorated_function

def supplier_required(f):
    """Decorator to require supplier role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.role or current_user.role.name not in ['supplier', 'admin']:
            abort(403)  # Forbidden
        
        return f(*args, **kwargs)
    return decorated_function

def consumer_required(f):
    """Decorator to require consumer role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.role or current_user.role.name not in ['consumer', 'admin']:
            abort(403)  # Forbidden
        
        return f(*args, **kwargs)
    return decorated_function

def email_verified_required(f):
    """Decorator to require email verification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.email_verified:
            flash('Please verify your email address to continue.', 'warning')
            return redirect(url_for('auth.verify_email'))
        
        return f(*args, **kwargs)
    return decorated_function

def active_user_required(f):
    """Decorator to require active user account"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=60, window=60):
    """
    Rate limiting decorator
    max_requests: Maximum number of requests allowed
    window: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (IP address or user ID)
            if current_user.is_authenticated:
                client_id = f"user_{current_user.id}"
            else:
                client_id = f"ip_{request.remote_addr}"
            
            now = time.time()
            
            # Clean old requests outside the window
            request_counts[client_id] = [
                req_time for req_time in request_counts[client_id]
                if now - req_time < window
            ]
            
            # Check if limit exceeded
            if len(request_counts[client_id]) >= max_requests:
                if request.is_json:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': f'Maximum {max_requests} requests per {window} seconds'
                    }), 429
                else:
                    abort(429)
            
            # Add current request
            request_counts[client_id].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def supplier_owns_product(f):
    """Decorator to ensure supplier owns the product they're accessing"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models import Product
        
        product_id = kwargs.get('product_id') or kwargs.get('id')
        if not product_id:
            abort(400)  # Bad Request
        
        product = Product.query.get_or_404(product_id)
        
        # Admin can access any product
        if current_user.role.name == 'admin':
            return f(*args, **kwargs)
        
        # Supplier can only access their own products
        if current_user.role.name == 'supplier' and product.supplier_id != current_user.id:
            abort(403)  # Forbidden
        
        return f(*args, **kwargs)
    return decorated_function

def user_owns_order(f):
    """Decorator to ensure user owns the order they're accessing"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models import Order
        
        order_id = kwargs.get('order_id') or kwargs.get('id')
        if not order_id:
            abort(400)  # Bad Request
        
        order = Order.query.get_or_404(order_id)
        
        # Admin can access any order
        if current_user.role.name == 'admin':
            return f(*args, **kwargs)
        
        # Supplier can access orders for their products
        if current_user.role.name == 'supplier' and order.supplier_id == current_user.id:
            return f(*args, **kwargs)
        
        # Consumer can only access their own orders
        if current_user.role.name == 'consumer' and order.user_id == current_user.id:
            return f(*args, **kwargs)
        
        abort(403)  # Forbidden
    return decorated_function

def api_key_required(f):
    """Decorator to require API key for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # In production, validate against database
        # For now, check against config
        from flask import current_app
        valid_api_key = current_app.config.get('API_KEY')
        
        if api_key != valid_api_key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def json_required(f):
    """Decorator to require JSON content type"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)
    return decorated_function

def validate_json_schema(schema):
    """Decorator to validate JSON request against schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                # Basic validation (can be extended with jsonschema library)
                for field in schema.get('required', []):
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Invalid JSON data'}), 400
        return decorated_function
    return decorator

def cache_response(timeout=300):
    """Decorator to cache response for specified timeout"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple in-memory cache (use Redis in production)
            cache_key = f"{f.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Check if response is cached
            # This is a simplified implementation
            # In production, use Flask-Caching or Redis
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_activity(activity_type):
    """Decorator to log user activity"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.models import UserActivity
            from app import db
            from datetime import datetime
            from flask import current_app
            
            # Execute the function first
            result = f(*args, **kwargs)
            
            # Log the activity if user is authenticated
            if current_user.is_authenticated:
                try:
                    activity = UserActivity(
                        user_id=current_user.id,
                        activity_type=activity_type,
                        ip_address=request.remote_addr,
                        user_agent=request.user_agent.string,
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(activity)
                    db.session.commit()
                except Exception as e:
                    # Don't let logging errors break the main function
                    current_app.logger.error(f"Activity logging failed: {str(e)}")
            
            return result
        return decorated_function
    return decorator

def measure_performance(f):
    """Decorator to measure function execution time"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        current_app.logger.info(f"{f.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    return decorated_function
