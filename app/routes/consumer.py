# Consumer Routes for MediPlant

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.database import db
from app.models import Product, Category, ShoppingCart, Wishlist, Order, ProductReview

consumer_bp = Blueprint('consumer', __name__)

@consumer_bp.route('/')
def home():
    """Homepage"""
    featured_products = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    categories = Category.query.filter_by(is_active=True).limit(6).all()
    
    return render_template('consumer/home.html', 
                         featured_products=featured_products, 
                         categories=categories)

@consumer_bp.route('/products')
def products():
    """Product listing page"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category')
    search_query = request.args.get('q', '')
    
    query = Product.query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search_query:
        query = query.filter(Product.name.contains(search_query))
    
    products = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('consumer/products.html', 
                         products=products, 
                         categories=categories,
                         current_category=category_id,
                         search_query=search_query)

@consumer_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = Product.query.filter_by(id=product_id, is_active=True).first_or_404()
    
    # Increment view count
    product.views_count += 1
    db.session.commit()
    
    # Get related products
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()
    
    # Get product reviews
    reviews = ProductReview.query.filter_by(
        product_id=product_id, 
        is_approved=True
    ).order_by(ProductReview.created_at.desc()).limit(10).all()
    
    return render_template('consumer/product_detail.html', 
                         product=product, 
                         related_products=related_products,
                         reviews=reviews)

@consumer_bp.route('/cart')
@login_required
def cart():
    """Shopping cart"""
    cart_items = ShoppingCart.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.get_current_price() * item.quantity for item in cart_items)
    
    return render_template('consumer/cart.html', cart_items=cart_items, total=total)

@consumer_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add item to cart"""
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    # Check if item already in cart
    cart_item = ShoppingCart.query.filter_by(
        user_id=current_user.id, 
        product_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = ShoppingCart(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Item added to cart!', 'success')
    
    return redirect(url_for('consumer.product_detail', product_id=product_id))

@consumer_bp.route('/cart/remove/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    """Remove item from cart"""
    cart_item = ShoppingCart.query.filter_by(
        id=cart_id, 
        user_id=current_user.id
    ).first_or_404()
    
    db.session.delete(cart_item)
    db.session.commit()
    
    flash('Item removed from cart.', 'info')
    return redirect(url_for('consumer.cart'))

@consumer_bp.route('/wishlist')
@login_required
def wishlist():
    """User wishlist"""
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('consumer/wishlist.html', wishlist_items=wishlist_items)

@consumer_bp.route('/wishlist/add/<int:product_id>')
@login_required
def add_to_wishlist(product_id):
    """Add item to wishlist"""
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(
        user_id=current_user.id, 
        product_id=product_id
    ).first()
    
    if not existing:
        wishlist_item = Wishlist(
            user_id=current_user.id,
            product_id=product_id
        )
        db.session.add(wishlist_item)
        db.session.commit()
        flash('Item added to wishlist!', 'success')
    else:
        flash('Item already in wishlist.', 'info')
    
    return redirect(url_for('consumer.product_detail', product_id=product_id))

@consumer_bp.route('/checkout')
@login_required
def checkout():
    """Checkout page"""
    cart_items = ShoppingCart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('consumer.cart'))
    
    total = sum(item.product.get_current_price() * item.quantity for item in cart_items)
    
    return render_template('consumer/checkout.html', cart_items=cart_items, total=total)

@consumer_bp.route('/orders')
@login_required
def orders():
    """User orders"""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id).order_by(
        Order.created_at.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('consumer/orders.html', orders=orders)

@consumer_bp.route('/profile')
@login_required
def profile():
    """User profile"""
    return render_template('consumer/profile.html')
