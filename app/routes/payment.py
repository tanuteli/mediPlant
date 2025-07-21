# Payment Routes for MediPlant

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.database import db
from app.models import Order, Payment
from datetime import datetime
import uuid
import hashlib
import hmac

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/order/<int:order_id>')
@login_required
def payment_page(order_id):
    """Payment page for order"""
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    
    if order.payment_status.value != 'pending':
        flash('Payment already processed for this order.', 'info')
        return redirect(url_for('order.detail', order_id=order_id))
    
    return render_template('payment/checkout.html', order=order)

@payment_bp.route('/process', methods=['POST'])
@login_required
def process_payment():
    """Process payment request"""
    order_id = request.form.get('order_id')
    payment_method = request.form.get('payment_method')
    
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    
    if order.payment_status.value != 'pending':
        return jsonify({'success': False, 'message': 'Payment already processed'})
    
    # Create payment record
    payment = Payment(
        payment_id=generate_payment_id(),
        order_id=order.id,
        user_id=current_user.id,
        amount=order.total_amount,
        currency='INR',
        payment_method=payment_method,
        gateway='razorpay'  # Default gateway
    )
    
    db.session.add(payment)
    
    if payment_method == 'razorpay':
        # Create Razorpay order
        razorpay_order = create_razorpay_order(order)
        payment.gateway_order_id = razorpay_order['id']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'payment_id': payment.payment_id,
            'razorpay_order_id': razorpay_order['id'],
            'amount': int(order.total_amount * 100),  # Razorpay amount in paise
            'currency': 'INR',
            'name': 'MediPlant',
            'description': f'Order #{order.order_number}',
            'prefill': {
                'name': current_user.name,
                'email': current_user.email,
                'contact': current_user.phone or ''
            }
        })
    
    elif payment_method == 'cod':
        # Cash on Delivery
        payment.status = 'pending'
        order.payment_status = 'pending'
        order.status = 'confirmed'
        
        db.session.commit()
        
        flash('Order placed successfully! Payment will be collected on delivery.', 'success')
        return jsonify({
            'success': True,
            'redirect': url_for('order.detail', order_id=order.id)
        })
    
    else:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Invalid payment method'})

@payment_bp.route('/verify', methods=['POST'])
@login_required
def verify_payment():
    """Verify payment callback from gateway"""
    payment_id = request.form.get('payment_id')
    gateway_payment_id = request.form.get('gateway_payment_id')
    gateway_order_id = request.form.get('gateway_order_id')
    gateway_signature = request.form.get('gateway_signature')
    
    payment = Payment.query.filter_by(
        payment_id=payment_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Verify signature
    if verify_razorpay_signature(gateway_order_id, gateway_payment_id, gateway_signature):
        # Payment successful
        payment.gateway_payment_id = gateway_payment_id
        payment.gateway_signature = gateway_signature
        payment.status = 'completed'
        payment.paid_at = datetime.utcnow()
        
        # Update order status
        order = payment.order
        order.payment_status = 'completed'
        order.status = 'confirmed'
        
        db.session.commit()
        
        flash('Payment successful! Your order has been confirmed.', 'success')
        return jsonify({
            'success': True,
            'redirect': url_for('order.detail', order_id=order.id)
        })
    else:
        # Payment verification failed
        payment.status = 'failed'
        db.session.commit()
        
        return jsonify({
            'success': False,
            'message': 'Payment verification failed'
        })

@payment_bp.route('/callback', methods=['POST'])
def payment_callback():
    """Payment gateway callback (webhook)"""
    # Handle payment gateway webhooks
    # This would be called by Razorpay/PayPal directly
    
    # Verify webhook signature
    signature = request.headers.get('X-Razorpay-Signature')
    payload = request.get_data()
    
    if not verify_webhook_signature(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 400
    
    data = request.json
    event = data.get('event')
    
    if event == 'payment.captured':
        # Handle successful payment
        payment_entity = data['payload']['payment']['entity']
        gateway_payment_id = payment_entity['id']
        
        payment = Payment.query.filter_by(
            gateway_payment_id=gateway_payment_id
        ).first()
        
        if payment and payment.status.value == 'pending':
            payment.status = 'completed'
            payment.paid_at = datetime.utcnow()
            
            order = payment.order
            order.payment_status = 'completed'
            order.status = 'confirmed'
            
            db.session.commit()
    
    elif event == 'payment.failed':
        # Handle failed payment
        payment_entity = data['payload']['payment']['entity']
        gateway_order_id = payment_entity['order_id']
        
        payment = Payment.query.filter_by(
            gateway_order_id=gateway_order_id
        ).first()
        
        if payment and payment.status.value == 'pending':
            payment.status = 'failed'
            db.session.commit()
    
    return jsonify({'status': 'ok'})

@payment_bp.route('/status/<payment_id>')
@login_required
def payment_status(payment_id):
    """Check payment status"""
    payment = Payment.query.filter_by(
        payment_id=payment_id,
        user_id=current_user.id
    ).first_or_404()
    
    return jsonify({
        'payment_id': payment.payment_id,
        'status': payment.status.value,
        'amount': float(payment.amount),
        'currency': payment.currency,
        'method': payment.payment_method,
        'created_at': payment.created_at.isoformat(),
        'paid_at': payment.paid_at.isoformat() if payment.paid_at else None
    })

def generate_payment_id():
    """Generate unique payment ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = str(uuid.uuid4())[:8].upper()
    return f'PAY{timestamp}{random_part}'

def create_razorpay_order(order):
    """Create Razorpay order"""
    # Mock implementation - replace with actual Razorpay API
    import random
    
    return {
        'id': f'order_{random.randint(100000, 999999)}',
        'amount': int(order.total_amount * 100),  # Amount in paise
        'currency': 'INR',
        'status': 'created'
    }

def verify_razorpay_signature(order_id, payment_id, signature):
    """Verify Razorpay payment signature"""
    # Mock implementation - replace with actual verification
    razorpay_key_secret = 'your_razorpay_key_secret'
    
    message = f'{order_id}|{payment_id}'
    expected_signature = hmac.new(
        razorpay_key_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # In production, use secure comparison
    return True  # Mock verification

def verify_webhook_signature(payload, signature):
    """Verify webhook signature"""
    # Mock implementation - replace with actual verification
    webhook_secret = 'your_webhook_secret'
    
    expected_signature = hmac.new(
        webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # In production, use secure comparison
    return True  # Mock verification
