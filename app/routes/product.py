# Product Routes for MediPlant

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.database import db
from app.models import Product, Category, ProductImage, ProductVariant

product_bp = Blueprint('product', __name__)

@product_bp.route('/')
def list_products():
    """List all products with filtering"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category')
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'created_at')
    
    query = Product.query.filter_by(is_active=True)
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search_query:
        query = query.filter(
            db.or_(
                Product.name.contains(search_query),
                Product.description.contains(search_query),
                Product.scientific_name.contains(search_query)
            )
        )
    
    # Apply sorting
    if sort_by == 'price_low':
        query = query.order_by(Product.base_price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.base_price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Product.rating_average.desc())
    elif sort_by == 'popular':
        query = query.order_by(Product.sales_count.desc())
    else:
        query = query.order_by(Product.created_at.desc())
    
    products = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('product/list.html', 
                         products=products, 
                         categories=categories,
                         current_category=category_id,
                         search_query=search_query,
                         sort_by=sort_by)

@product_bp.route('/<int:product_id>')
def detail(product_id):
    """Product detail page"""
    product = Product.query.filter_by(id=product_id, is_active=True).first_or_404()
    
    # Increment view count
    product.views_count += 1
    db.session.commit()
    
    # Get product images
    images = ProductImage.query.filter_by(product_id=product_id).order_by(
        ProductImage.is_primary.desc(), ProductImage.sort_order.asc()
    ).all()
    
    # Get product variants
    variants = ProductVariant.query.filter_by(
        product_id=product_id, is_active=True
    ).all()
    
    # Get related products
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()
    
    return render_template('product/detail.html', 
                         product=product,
                         images=images,
                         variants=variants,
                         related_products=related_products)

@product_bp.route('/search')
def search():
    """Product search"""
    query = request.args.get('q', '')
    category_id = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    if not query and not category_id:
        return render_template('product/search.html', products=[], query='')
    
    # Build search query
    search_query = Product.query.filter_by(is_active=True)
    
    if query:
        search_query = search_query.filter(
            db.or_(
                Product.name.contains(query),
                Product.description.contains(query),
                Product.scientific_name.contains(query),
                Product.benefits.contains(query)
            )
        )
    
    if category_id:
        search_query = search_query.filter_by(category_id=category_id)
    
    if min_price:
        search_query = search_query.filter(Product.base_price >= min_price)
    
    if max_price:
        search_query = search_query.filter(Product.base_price <= max_price)
    
    products = search_query.order_by(Product.sales_count.desc()).limit(50).all()
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('product/search.html', 
                         products=products, 
                         query=query,
                         categories=categories,
                         selected_category=category_id)

@product_bp.route('/category/<int:category_id>')
def by_category(category_id):
    """Products by category"""
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    
    products = Product.query.filter_by(
        category_id=category_id, 
        is_active=True
    ).order_by(Product.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('product/category.html', 
                         category=category, 
                         products=products)

@product_bp.route('/featured')
def featured():
    """Featured products"""
    products = Product.query.filter_by(
        is_featured=True, 
        is_active=True
    ).order_by(Product.created_at.desc()).all()
    
    return render_template('product/featured.html', products=products)

@product_bp.route('/api/<int:product_id>/variants')
def api_variants(product_id):
    """API endpoint to get product variants"""
    variants = ProductVariant.query.filter_by(
        product_id=product_id, 
        is_active=True
    ).all()
    
    variants_data = []
    for variant in variants:
        variants_data.append({
            'id': variant.id,
            'name': variant.name,
            'price': float(variant.price),
            'stock_quantity': variant.stock_quantity
        })
    
    return jsonify(variants_data)

@product_bp.route('/api/<int:product_id>/check-stock')
def api_check_stock(product_id):
    """API endpoint to check product stock"""
    product = Product.query.get_or_404(product_id)
    variant_id = request.args.get('variant_id', type=int)
    
    if variant_id:
        variant = ProductVariant.query.filter_by(
            id=variant_id, 
            product_id=product_id
        ).first()
        stock = variant.stock_quantity if variant else 0
    else:
        stock = product.stock_quantity
    
    return jsonify({
        'in_stock': stock > 0,
        'stock_quantity': stock,
        'max_order_quantity': min(stock, product.max_order_quantity)
    })
