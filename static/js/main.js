// MediPlant Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeQuantitySelectors();
    initializeAnimations();
    initializeTooltips();
    initializeImageLazyLoading();
    initializeFormValidation();
    
    // Auto-hide flash messages
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Quantity Selector Functionality
function initializeQuantitySelectors() {
    const quantitySelectors = document.querySelectorAll('.quantity-selector');
    
    quantitySelectors.forEach(function(selector) {
        const decreaseBtn = selector.querySelector('.quantity-decrease');
        const increaseBtn = selector.querySelector('.quantity-increase');
        const input = selector.querySelector('.quantity-input');
        
        if (decreaseBtn && increaseBtn && input) {
            decreaseBtn.addEventListener('click', function() {
                let value = parseInt(input.value);
                if (value > 1) {
                    input.value = value - 1;
                    updateCartQuantity(input);
                }
            });
            
            increaseBtn.addEventListener('click', function() {
                let value = parseInt(input.value);
                const max = parseInt(input.getAttribute('max')) || 99;
                if (value < max) {
                    input.value = value + 1;
                    updateCartQuantity(input);
                }
            });
            
            input.addEventListener('change', function() {
                let value = parseInt(this.value);
                const min = parseInt(this.getAttribute('min')) || 1;
                const max = parseInt(this.getAttribute('max')) || 99;
                
                if (isNaN(value) || value < min) {
                    this.value = min;
                } else if (value > max) {
                    this.value = max;
                }
                
                updateCartQuantity(this);
            });
        }
    });
}

// Update cart quantity via AJAX
function updateCartQuantity(input) {
    const cartItemId = input.getAttribute('data-cart-id');
    const quantity = parseInt(input.value);
    
    if (cartItemId) {
        // Here you can add AJAX call to update cart quantity
        console.log(`Updating cart item ${cartItemId} to quantity ${quantity}`);
        
        // Show loading state
        input.classList.add('loading');
        
        // Simulate API call
        setTimeout(function() {
            input.classList.remove('loading');
            showToast('Cart updated successfully!', 'success');
            updateCartTotal();
        }, 500);
    }
}

// Animation Initialization
function initializeAnimations() {
    // Scroll animations
    const animatedElements = document.querySelectorAll('.fade-in-up');
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    animatedElements.forEach(function(element) {
        observer.observe(element);
    });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Lazy loading for images
function initializeImageLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(function(img) {
        imageObserver.observe(img);
    });
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

// Add to cart functionality
function addToCart(productId, quantity = 1) {
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('quantity', quantity);
    
    // Show loading state
    const addButton = document.querySelector(`[onclick*="${productId}"]`);
    if (addButton) {
        const originalText = addButton.innerHTML;
        addButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
        addButton.disabled = true;
        
        // Simulate API call
        setTimeout(function() {
            addButton.innerHTML = '<i class="fas fa-check"></i> Added!';
            setTimeout(function() {
                addButton.innerHTML = originalText;
                addButton.disabled = false;
            }, 2000);
        }, 1000);
    }
    
    showToast('Product added to cart!', 'success');
    updateCartCounter();
}

// Add to wishlist functionality
function addToWishlist(productId) {
    console.log(`Adding product ${productId} to wishlist`);
    
    const wishlistButton = document.querySelector(`[onclick*="addToWishlist(${productId})"]`);
    if (wishlistButton) {
        const icon = wishlistButton.querySelector('i');
        if (icon.classList.contains('far')) {
            icon.classList.remove('far');
            icon.classList.add('fas');
            wishlistButton.classList.add('text-danger');
            showToast('Added to wishlist!', 'success');
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
            wishlistButton.classList.remove('text-danger');
            showToast('Removed from wishlist!', 'info');
        }
    }
}

// Remove from cart
function removeFromCart(cartId) {
    if (confirm('Are you sure you want to remove this item from your cart?')) {
        const cartItem = document.querySelector(`[data-cart-id="${cartId}"]`).closest('.cart-item');
        
        // Animate removal
        cartItem.style.transition = 'all 0.3s ease';
        cartItem.style.opacity = '0';
        cartItem.style.transform = 'translateX(-100%)';
        
        setTimeout(function() {
            cartItem.remove();
            updateCartTotal();
            showToast('Item removed from cart!', 'info');
            updateCartCounter();
        }, 300);
    }
}

// Update cart total
function updateCartTotal() {
    const cartItems = document.querySelectorAll('.cart-item');
    let total = 0;
    
    cartItems.forEach(function(item) {
        const priceElement = item.querySelector('.item-price');
        const quantityElement = item.querySelector('.quantity-input');
        
        if (priceElement && quantityElement) {
            const price = parseFloat(priceElement.textContent.replace('₹', '').replace(',', ''));
            const quantity = parseInt(quantityElement.value);
            total += price * quantity;
        }
    });
    
    const totalElement = document.querySelector('.cart-total');
    if (totalElement) {
        totalElement.textContent = `₹${total.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    }
}

// Update cart counter in navigation
function updateCartCounter() {
    const counter = document.querySelector('.cart-counter');
    if (counter) {
        let count = parseInt(counter.textContent) || 0;
        counter.textContent = count + 1;
        
        // Animate counter
        counter.classList.add('animate-pulse');
        setTimeout(function() {
            counter.classList.remove('animate-pulse');
        }, 1000);
    }
}

// Toast notification system
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toastElement = document.createElement('div');
    toastElement.className = `toast align-items-center text-white bg-${type} border-0`;
    toastElement.setAttribute('role', 'alert');
    toastElement.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${getToastIcon(type)} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastElement);
    
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000
    });
    
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1060';
    document.body.appendChild(container);
    return container;
}

function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Search functionality
function performSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    const searchTerm = searchInput.value.trim();
    
    if (searchTerm.length >= 2) {
        window.location.href = `/products?search=${encodeURIComponent(searchTerm)}`;
    } else {
        showToast('Please enter at least 2 characters to search', 'warning');
    }
}

// Filter products
function filterProducts(category) {
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('category', category);
    window.location.href = currentUrl.toString();
}

// Price range filter
function updatePriceRange() {
    const minPrice = document.querySelector('#minPrice').value;
    const maxPrice = document.querySelector('#maxPrice').value;
    
    const currentUrl = new URL(window.location.href);
    if (minPrice) currentUrl.searchParams.set('min_price', minPrice);
    if (maxPrice) currentUrl.searchParams.set('max_price', maxPrice);
    
    window.location.href = currentUrl.toString();
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Back to top button
window.addEventListener('scroll', function() {
    const backToTopButton = document.querySelector('.back-to-top');
    if (backToTopButton) {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    }
});

// Create back to top button
function createBackToTopButton() {
    const button = document.createElement('button');
    button.className = 'btn btn-primary back-to-top';
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.onclick = function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    
    document.body.appendChild(button);
}

// Initialize back to top button
createBackToTopButton();

// Product image gallery
function initializeProductGallery() {
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    const mainImage = document.querySelector('.product-main-image');
    
    thumbnails.forEach(function(thumbnail) {
        thumbnail.addEventListener('click', function() {
            // Remove active class from all thumbnails
            thumbnails.forEach(function(thumb) {
                thumb.classList.remove('active');
            });
            
            // Add active class to clicked thumbnail
            this.classList.add('active');
            
            // Update main image
            if (mainImage) {
                mainImage.src = this.src;
                mainImage.alt = this.alt;
            }
        });
    });
}

// Initialize product gallery if on product page
if (document.querySelector('.product-thumbnail')) {
    initializeProductGallery();
}

// Newsletter subscription
function subscribeNewsletter() {
    const emailInput = document.querySelector('#newsletter-email');
    const email = emailInput.value.trim();
    
    if (email && isValidEmail(email)) {
        // Simulate API call
        showToast('Thank you for subscribing to our newsletter!', 'success');
        emailInput.value = '';
    } else {
        showToast('Please enter a valid email address', 'danger');
    }
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Print order functionality
function printOrder() {
    window.print();
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    }).catch(function() {
        showToast('Failed to copy to clipboard', 'danger');
    });
}

// Loading state management
function showLoading(element) {
    if (element) {
        element.classList.add('loading');
        element.disabled = true;
    }
}

function hideLoading(element) {
    if (element) {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Utility function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Export functions for global use
window.MediPlant = {
    addToCart,
    addToWishlist,
    removeFromCart,
    showToast,
    formatCurrency,
    formatDate,
    performSearch,
    filterProducts,
    subscribeNewsletter,
    printOrder,
    copyToClipboard
};
