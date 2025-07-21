// MediPlant Main JavaScript

// Global variables
let cart = JSON.parse(localStorage.getItem('mediplant_cart')) || [];
let wishlist = JSON.parse(localStorage.getItem('mediplant_wishlist')) || [];

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    updateCartCount();
    updateWishlistCount();
});

// Initialize application
function initializeApp() {
    // Add loading states to buttons
    setupButtonLoadingStates();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Setup form validations
    setupFormValidations();
    
    // Initialize product interactions
    setupProductInteractions();
    
    // Setup search functionality
    setupSearch();
    
    // Setup notification system
    setupNotifications();
}

// Button loading states
function setupButtonLoadingStates() {
    document.querySelectorAll('button[type="submit"], .btn-loading-enabled').forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.form && !this.form.checkValidity()) return;
            
            const originalText = this.innerHTML;
            this.classList.add('btn-loading');
            this.disabled = true;
            
            // Reset after 3 seconds if no form submission
            setTimeout(() => {
                this.classList.remove('btn-loading');
                this.disabled = false;
                this.innerHTML = originalText;
            }, 3000);
        });
    });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Form validation setup
function setupFormValidations() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showNotification('Please fill in all required fields correctly.', 'error');
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Product interactions (add to cart, wishlist, etc.)
function setupProductInteractions() {
    // Add to cart buttons
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const productName = this.dataset.productName;
            const productPrice = this.dataset.productPrice;
            const productImage = this.dataset.productImage;
            
            addToCart({
                id: productId,
                name: productName,
                price: parseFloat(productPrice),
                image: productImage,
                quantity: 1
            });
        });
    });
    
    // Add to wishlist buttons
    document.querySelectorAll('.add-to-wishlist').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            toggleWishlist(productId, this);
        });
    });
    
    // Quick view buttons
    document.querySelectorAll('.quick-view').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            showQuickView(productId);
        });
    });
}

// Cart management
function addToCart(product) {
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
        existingItem.quantity += 1;
        showNotification(`Updated ${product.name} quantity in cart`, 'success');
    } else {
        cart.push(product);
        showNotification(`${product.name} added to cart`, 'success');
    }
    
    saveCart();
    updateCartCount();
    animateCartIcon();
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
    updateCartCount();
    showNotification('Item removed from cart', 'info');
}

function updateCartQuantity(productId, quantity) {
    const item = cart.find(item => item.id === productId);
    if (item) {
        if (quantity <= 0) {
            removeFromCart(productId);
        } else {
            item.quantity = quantity;
            saveCart();
            updateCartCount();
        }
    }
}

function saveCart() {
    localStorage.setItem('mediplant_cart', JSON.stringify(cart));
}

function updateCartCount() {
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    const cartCountElements = document.querySelectorAll('#cart-count');
    cartCountElements.forEach(element => {
        element.textContent = count;
        element.style.display = count > 0 ? 'inline' : 'none';
    });
}

// Wishlist management
function toggleWishlist(productId, button) {
    const isInWishlist = wishlist.includes(productId);
    
    if (isInWishlist) {
        wishlist = wishlist.filter(id => id !== productId);
        button.innerHTML = '<i class="far fa-heart"></i>';
        button.classList.remove('text-danger');
        showNotification('Removed from wishlist', 'info');
    } else {
        wishlist.push(productId);
        button.innerHTML = '<i class="fas fa-heart"></i>';
        button.classList.add('text-danger');
        showNotification('Added to wishlist', 'success');
    }
    
    saveWishlist();
    updateWishlistCount();
}

function saveWishlist() {
    localStorage.setItem('mediplant_wishlist', JSON.stringify(wishlist));
}

function updateWishlistCount() {
    const count = wishlist.length;
    const wishlistCountElements = document.querySelectorAll('#wishlist-count');
    wishlistCountElements.forEach(element => {
        element.textContent = count;
        element.style.display = count > 0 ? 'inline' : 'none';
    });
}

// Search functionality
function setupSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchForm = document.querySelector('form[action*="search"]');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    showSearchSuggestions(query);
                }, 300);
            } else {
                hideSearchSuggestions();
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target)) {
                hideSearchSuggestions();
            }
        });
    }
}

function showSearchSuggestions(query) {
    // This would typically make an AJAX call to get suggestions
    const suggestions = [
        'Turmeric powder',
        'Aloe vera gel',
        'Ashwagandha capsules',
        'Neem oil',
        'Chamomile tea'
    ].filter(item => item.toLowerCase().includes(query.toLowerCase()));
    
    if (suggestions.length > 0) {
        createSuggestionsDropdown(suggestions);
    }
}

function createSuggestionsDropdown(suggestions) {
    const existingDropdown = document.querySelector('.search-suggestions');
    if (existingDropdown) {
        existingDropdown.remove();
    }
    
    const dropdown = document.createElement('div');
    dropdown.className = 'search-suggestions position-absolute bg-white border rounded shadow-sm w-100';
    dropdown.style.top = '100%';
    dropdown.style.zIndex = '1000';
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'suggestion-item p-2 border-bottom';
        item.style.cursor = 'pointer';
        item.textContent = suggestion;
        
        item.addEventListener('click', function() {
            document.querySelector('.search-input').value = suggestion;
            hideSearchSuggestions();
            document.querySelector('form[action*="search"]').submit();
        });
        
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'transparent';
        });
        
        dropdown.appendChild(item);
    });
    
    const searchContainer = document.querySelector('.search-input').parentElement;
    searchContainer.style.position = 'relative';
    searchContainer.appendChild(dropdown);
}

function hideSearchSuggestions() {
    const dropdown = document.querySelector('.search-suggestions');
    if (dropdown) {
        dropdown.remove();
    }
}

// Notification system
function setupNotifications() {
    // Create notification container if it doesn't exist
    if (!document.querySelector('.notification-container')) {
        const container = document.createElement('div');
        container.className = 'notification-container position-fixed';
        container.style.top = '100px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
}

function showNotification(message, type = 'info', duration = 3000) {
    const container = document.querySelector('.notification-container');
    const notification = document.createElement('div');
    
    const typeClasses = {
        success: 'alert-success',
        error: 'alert-danger',
        warning: 'alert-warning',
        info: 'alert-info'
    };
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-triangle',
        warning: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    notification.className = `alert ${typeClasses[type]} alert-dismissible fade show mb-2`;
    notification.style.minWidth = '300px';
    notification.innerHTML = `
        <i class="fas ${icons[type]} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, duration);
}

// Animation helpers
function animateCartIcon() {
    const cartIcon = document.querySelector('.fa-shopping-cart');
    if (cartIcon) {
        cartIcon.style.animation = 'none';
        cartIcon.offsetHeight; // Trigger reflow
        cartIcon.style.animation = 'bounce 0.6s ease';
        
        setTimeout(() => {
            cartIcon.style.animation = '';
        }, 600);
    }
}

// Quick view modal
function showQuickView(productId) {
    // This would typically fetch product data via AJAX
    const modalHtml = `
        <div class="modal fade" id="quickViewModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header border-0">
                        <h5 class="modal-title">Quick View</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <img src="/static/images/products/placeholder.jpg" class="img-fluid rounded" alt="Product">
                            </div>
                            <div class="col-md-6">
                                <h4>Product Name</h4>
                                <p class="text-muted">Product description goes here...</p>
                                <div class="rating mb-3">
                                    <i class="fas fa-star text-warning"></i>
                                    <i class="fas fa-star text-warning"></i>
                                    <i class="fas fa-star text-warning"></i>
                                    <i class="fas fa-star text-warning"></i>
                                    <i class="far fa-star text-warning"></i>
                                    <span class="ms-2">(4.0)</span>
                                </div>
                                <h5 class="text-sage-green mb-3">₹299</h5>
                                <div class="d-grid gap-2">
                                    <button class="btn btn-sage-green">Add to Cart</button>
                                    <button class="btn btn-outline-sage">Add to Wishlist</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal
    const existingModal = document.querySelector('#quickViewModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add new modal
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.querySelector('#quickViewModal'));
    modal.show();
    
    // Remove modal from DOM when hidden
    document.querySelector('#quickViewModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// AJAX helper
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    return fetch(url, { ...defaultOptions, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Request failed:', error);
            showNotification('Something went wrong. Please try again.', 'error');
            throw error;
        });
}

// Export functions for global use
window.MediPlant = {
    addToCart,
    removeFromCart,
    updateCartQuantity,
    toggleWishlist,
    showNotification,
    showQuickView,
    formatCurrency,
    makeRequest
};

// Scroll animations for landing page
function initializeScrollAnimations() {
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    animateElements.forEach((el) => {
        observer.observe(el);
    });
}

// Counter animations for stats
function initializeCounters() {
    const counters = document.querySelectorAll('.stat-number[data-count]');
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-count'));
                animateCounter(counter, target);
                counterObserver.unobserve(counter);
            }
        });
    }, {
        threshold: 0.5
    });
    
    counters.forEach((counter) => {
        counterObserver.observe(counter);
    });
}

// Animate counter from 0 to target
function animateCounter(element, target) {
    let start = 0;
    const duration = 2000;
    const increment = target / (duration / 16);
    
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(start).toLocaleString();
        }
    }, 16);
}

// Initialize animations on index page
if (window.location.pathname === '/' || window.location.pathname === '/index') {
    document.addEventListener('DOMContentLoaded', function() {
        initializeScrollAnimations();
        initializeCounters();
    });
}
