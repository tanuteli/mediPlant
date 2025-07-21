from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        newsletter = request.form.get('newsletter')
        
        # Here you would typically save to database or send email
        # For now, just show a success message
        flash('Thank you for your message! We\'ll get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')

@main_bp.route('/api/newsletter/subscribe', methods=['POST'])
def subscribe_newsletter():
    """Newsletter subscription endpoint"""
    email = request.json.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'})
    
    # Here you would typically save to database
    # For now, just return success
    return jsonify({'success': True, 'message': 'Successfully subscribed to newsletter!'})
