# Order Routes for MediPlant

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.database import db
from app.models import Order, OrderItem, ShoppingCart, Product
from datetime import datetime
import uuid

order_bp = Blueprint('order', __name__)

@order_bp.route('/create', methods=['POST'])
@login_required
def create_order():
    """Create new order from cart"""
    cart_items = ShoppingCart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('consumer.cart'))
    
    # Group items by supplier
    supplier_items = {}
    for item in cart_items:
        supplier_id = item.product.supplier_id
        if supplier_id not in supplier_items:
            supplier_items[supplier_id] = []
        supplier_items[supplier_id].append(item)
    
    created_orders = []
    
    # Create separate order for each supplier
    for supplier_id, items in supplier_items.items():
        # Calculate totals
        subtotal = sum(item.product.get_current_price() * item.quantity for item in items)
        tax_amount = subtotal * 0.18  # 18% tax
        shipping_amount = 50.0 if subtotal < 500 else 0  # Free shipping above 500
        total_amount = subtotal + tax_amount + shipping_amount
        
        # Create order
        order = Order(
            order_number=generate_order_number(),
            user_id=current_user.id,
            supplier_id=supplier_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_amount=shipping_amount,
            total_amount=total_amount,
            shipping_address=get_shipping_address(),
            billing_address=get_billing_address()
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items
        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.product.get_current_price(),
                total_price=item.product.get_current_price() * item.quantity,
                product_name=item.product.name,
                product_sku=item.product.sku,
                supplier_id=supplier_id
            )
            db.session.add(order_item)
            
            # Update product stock
            item.product.stock_quantity -= item.quantity
            item.product.sales_count += item.quantity
        
        created_orders.append(order)
    
    # Clear cart
    ShoppingCart.query.filter_by(user_id=current_user.id).delete()
    
    db.session.commit()
    
    if len(created_orders) == 1:
        flash(f'Order {created_orders[0].order_number} created successfully!', 'success')
        return redirect(url_for('order.detail', order_id=created_orders[0].id))
    else:
        flash(f'{len(created_orders)} orders created successfully!', 'success')
        return redirect(url_for('consumer.orders'))

@order_bp.route('/<int:order_id>')
@login_required
def detail(order_id):
    """Order detail page"""
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('order/detail.html', order=order)

@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancel order"""
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    
    if order.status.value not in ['pending', 'confirmed']:
        flash('Order cannot be cancelled at this stage.', 'error')
        return redirect(url_for('order.detail', order_id=order_id))
    
    order.status = 'cancelled'
    
    # Restore product stock
    for item in order.items:
        product = Product.query.get(item.product_id)
        if product:
            product.stock_quantity += item.quantity
            product.sales_count -= item.quantity
    
    db.session.commit()
    
    flash('Order cancelled successfully.', 'info')
    return redirect(url_for('order.detail', order_id=order_id))

@order_bp.route('/<int:order_id>/track')
@login_required
def track(order_id):
    """Order tracking page"""
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('order/track.html', order=order)

@order_bp.route('/api/<int:order_id>/status')
@login_required
def api_order_status(order_id):
    """API endpoint for order status"""
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    
    return jsonify({
        'order_number': order.order_number,
        'status': order.status.value,
        'payment_status': order.payment_status.value,
        'tracking_number': order.tracking_number,
        'created_at': order.created_at.isoformat(),
        'total_amount': float(order.total_amount)
    })

def generate_order_number():
    """Generate unique order number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = str(uuid.uuid4())[:8].upper()
    return f'MP{timestamp}{random_part}'

def get_shipping_address():
    """Get shipping address from user"""
    # TODO: Implement address selection from user addresses
    return {
        'name': current_user.name,
        'phone': current_user.phone or '',
        'address_line1': 'Sample Address Line 1',
        'city': 'Sample City',
        'state': 'Sample State',
        'postal_code': '123456',
        'country': 'India'
    }

def get_billing_address():
    """Get billing address from user"""
    # For now, same as shipping address
    return get_shipping_address()
