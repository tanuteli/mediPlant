# Review Routes for MediPlant

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.database import db
from app.models import Review, Product, Order, OrderItem
from datetime import datetime

review_bp = Blueprint('review', __name__)

@review_bp.route('/add/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_review(product_id):
    """Add review for a product"""
    product = Product.query.get_or_404(product_id)
    
    # Check if user has purchased this product
    has_purchased = db.session.query(OrderItem).join(Order).filter(
        Order.user_id == current_user.id,
        OrderItem.product_id == product_id,
        Order.status.in_(['delivered', 'completed'])
    ).first()
    
    if not has_purchased:
        flash('You can only review products you have purchased.', 'warning')
        return redirect(url_for('product.detail', id=product_id))
    
    # Check if user has already reviewed this product
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this product.', 'info')
        return redirect(url_for('product.detail', id=product_id))
    
    if request.method == 'POST':
        rating = int(request.form.get('rating', 0))
        title = request.form.get('title', '').strip()
        comment = request.form.get('comment', '').strip()
        
        # Validation
        if not (1 <= rating <= 5):
            flash('Please provide a valid rating between 1 and 5.', 'error')
            return render_template('review/add.html', product=product)
        
        if not title:
            flash('Please provide a review title.', 'error')
            return render_template('review/add.html', product=product)
        
        if not comment:
            flash('Please provide a review comment.', 'error')
            return render_template('review/add.html', product=product)
        
        # Create review
        review = Review(
            user_id=current_user.id,
            product_id=product_id,
            rating=rating,
            title=title,
            comment=comment,
            is_verified_purchase=True
        )
        
        db.session.add(review)
        
        # Update product rating
        update_product_rating(product_id)
        
        db.session.commit()
        
        flash('Your review has been added successfully!', 'success')
        return redirect(url_for('product.detail', id=product_id))
    
    return render_template('review/add.html', product=product)

@review_bp.route('/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    """Edit user's own review"""
    review = Review.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        rating = int(request.form.get('rating', 0))
        title = request.form.get('title', '').strip()
        comment = request.form.get('comment', '').strip()
        
        # Validation
        if not (1 <= rating <= 5):
            flash('Please provide a valid rating between 1 and 5.', 'error')
            return render_template('review/edit.html', review=review)
        
        if not title:
            flash('Please provide a review title.', 'error')
            return render_template('review/edit.html', review=review)
        
        if not comment:
            flash('Please provide a review comment.', 'error')
            return render_template('review/edit.html', review=review)
        
        # Update review
        review.rating = rating
        review.title = title
        review.comment = comment
        review.updated_at = datetime.utcnow()
        
        # Update product rating
        update_product_rating(review.product_id)
        
        db.session.commit()
        
        flash('Your review has been updated successfully!', 'success')
        return redirect(url_for('product.detail', id=review.product_id))
    
    return render_template('review/edit.html', review=review)

@review_bp.route('/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    """Delete user's own review"""
    review = Review.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()
    
    product_id = review.product_id
    
    db.session.delete(review)
    
    # Update product rating
    update_product_rating(product_id)
    
    db.session.commit()
    
    flash('Your review has been deleted.', 'info')
    return redirect(url_for('product.detail', id=product_id))

@review_bp.route('/product/<int:product_id>')
def product_reviews(product_id):
    """Get all reviews for a product"""
    product = Product.query.get_or_404(product_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    reviews = Review.query.filter_by(product_id=product_id)\
        .order_by(Review.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('review/product_reviews.html', 
                         product=product, reviews=reviews)

@review_bp.route('/api/product/<int:product_id>')
def api_product_reviews(product_id):
    """API endpoint for product reviews"""
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    reviews = Review.query.filter_by(product_id=product_id)\
        .order_by(Review.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'reviews': [{
            'id': review.id,
            'user_name': review.user.name,
            'rating': review.rating,
            'title': review.title,
            'comment': review.comment,
            'created_at': review.created_at.isoformat(),
            'is_verified_purchase': review.is_verified_purchase
        } for review in reviews.items],
        'total': reviews.total,
        'pages': reviews.pages,
        'current_page': page,
        'has_next': reviews.has_next,
        'has_prev': reviews.has_prev
    })

@review_bp.route('/helpful/<int:review_id>', methods=['POST'])
@login_required
def mark_helpful(review_id):
    """Mark review as helpful"""
    review = Review.query.get_or_404(review_id)
    
    # Check if user has already marked this review
    # This would require a separate table for review helpfulness
    # For now, just increment the helpful count
    
    review.helpful_count += 1
    db.session.commit()
    
    return jsonify({
        'success': True,
        'helpful_count': review.helpful_count
    })

@review_bp.route('/report/<int:review_id>', methods=['POST'])
@login_required
def report_review(review_id):
    """Report inappropriate review"""
    review = Review.query.get_or_404(review_id)
    reason = request.form.get('reason', '').strip()
    
    if not reason:
        return jsonify({
            'success': False,
            'message': 'Please provide a reason for reporting.'
        })
    
    # In a real application, you would store the report in a separate table
    # and notify moderators
    
    # For now, just log it
    from flask import current_app
    current_app.logger.info(f"Review {review_id} reported by user {current_user.id}: {reason}")
    
    return jsonify({
        'success': True,
        'message': 'Review reported successfully. Our team will review it.'
    })

@review_bp.route('/user/<int:user_id>')
@login_required
def user_reviews(user_id):
    """Get all reviews by a user (only viewable by the user themselves)"""
    if current_user.id != user_id and not current_user.is_admin():
        flash('You can only view your own reviews.', 'warning')
        return redirect(url_for('consumer.profile'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    reviews = Review.query.filter_by(user_id=user_id)\
        .order_by(Review.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('review/user_reviews.html', reviews=reviews)

def update_product_rating(product_id):
    """Update product's average rating and review count"""
    from sqlalchemy import func
    
    result = db.session.query(
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).filter_by(product_id=product_id).first()
    
    product = Product.query.get(product_id)
    if product:
        product.average_rating = round(result.avg_rating or 0, 1)
        product.review_count = result.review_count or 0

def calculate_rating_distribution(product_id):
    """Calculate rating distribution for a product"""
    from sqlalchemy import func
    
    distribution = db.session.query(
        Review.rating,
        func.count(Review.id).label('count')
    ).filter_by(product_id=product_id)\
     .group_by(Review.rating)\
     .all()
    
    # Create distribution dict with all ratings 1-5
    rating_dist = {i: 0 for i in range(1, 6)}
    for rating, count in distribution:
        rating_dist[rating] = count
    
    total_reviews = sum(rating_dist.values())
    
    # Calculate percentages
    if total_reviews > 0:
        for rating in rating_dist:
            rating_dist[rating] = {
                'count': rating_dist[rating],
                'percentage': round((rating_dist[rating] / total_reviews) * 100, 1)
            }
    
    return rating_dist
