// Authentication related JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeAuthFeatures();
});

function initializeAuthFeatures() {
    // Form validation with enhanced UX
    initializeFormValidation();
    
    // Password strength indicator
    initializePasswordStrength();
    
    // Username availability check
    initializeUsernameCheck();
    
    // Session management
    initializeSessionManagement();
    
    // Auto-logout after inactivity
    initializeAutoLogout();
    
    // Password visibility toggle
    initializePasswordToggle();
    
    // Terms agreement validation
    initializeTermsValidation();
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showNotification('Please fix the errors before submitting', 'error');
            } else {
                // Show loading state
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    setButtonLoading(submitBtn, true);
                }
            }
        });
        
        // Real-time validation on input blur
        const inputs = form.querySelectorAll('input[required], select[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
                // Real-time validation for specific fields
                if (this.type === 'email' || this.name === 'email') {
                    validateEmailField(this);
                }
                if (this.type === 'password' && this.id !== 'confirm_password') {
                    updatePasswordStrength(this.value, this);
                }
                if (this.id === 'confirm_password') {
                    validatePasswordMatch(this);
                }
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    // Special validation for password confirmation
    const password = form.querySelector('#password');
    const confirmPassword = form.querySelector('#confirm_password');
    if (password && confirmPassword && confirmPassword.value) {
        if (password.value !== confirmPassword.value) {
            showFieldError(confirmPassword, 'Passwords do not match');
            isValid = false;
        }
    }
    
    // Terms agreement validation
    const termsCheckbox = form.querySelector('#terms');
    if (termsCheckbox && !termsCheckbox.checked) {
        showNotification('Please agree to the terms and conditions', 'error');
        isValid = false;
    }
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    
    // Clear previous errors
    clearFieldError(field);
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        isValid = false;
    }
    
    // Email validation
    if ((field.type === 'email' || field.name === 'email') && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    }
    
    // Username validation
    if ((field.name === 'username' || field.id === 'id_username') && value) {
        if (value.length < 3) {
            showFieldError(field, 'Username must be at least 3 characters long');
            isValid = false;
        }
        if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            showFieldError(field, 'Username can only contain letters, numbers, and underscores');
            isValid = false;
        }
    }
    
    // Password validation
    if (field.type === 'password' && field.id !== 'confirm_password' && value) {
        if (value.length < 8) {
            showFieldError(field, 'Password must be at least 8 characters long');
            isValid = false;
        }
    }
    
    if (isValid) {
        field.classList.add('success');
        field.classList.remove('error');
    }
    
    return isValid;
}

function validateEmailField(field) {
    const value = field.value.trim();
    if (!value) return true;
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
}

function validatePasswordMatch(field) {
    const password = document.querySelector('#password');
    if (!password || !field.value) return true;
    
    return password.value === field.value;
}

function showFieldError(field, message) {
    field.classList.add('error');
    field.classList.remove('success');
    
    let errorElement = field.parentNode.querySelector('.form-error');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'form-error';
        field.parentNode.appendChild(errorElement);
    }
    
    errorElement.innerHTML = `<i class="fas fa-exclamation-circle error-icon"></i> ${message}`;
    errorElement.style.display = 'block';
}

function clearFieldError(field) {
    field.classList.remove('error', 'success');
    const errorElement = field.parentNode.querySelector('.form-error');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

function initializePasswordStrength() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        if (input.id !== 'confirm_password') {
            input.addEventListener('input', function() {
                updatePasswordStrength(this.value, this);
            });
        }
    });
}

function updatePasswordStrength(password, input) {
    let strength = 0;
    const feedback = [];
    
    // Length check
    if (password.length >= 8) {
        strength++;
    } else {
        feedback.push('at least 8 characters');
    }
    
    // Lowercase and uppercase check
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) {
        strength++;
    } else {
        feedback.push('both lowercase and uppercase letters');
    }
    
    // Number check
    if (password.match(/\d/)) {
        strength++;
    } else {
        feedback.push('at least one number');
    }
    
    // Special character check
    if (password.match(/[^a-zA-Z\d]/)) {
        strength++;
    } else {
        feedback.push('at least one special character');
    }
    
    // Update UI
    const container = input.closest('.form-group');
    if (!container) return;
    
    let strengthIndicator = container.querySelector('.password-strength');
    if (!strengthIndicator) {
        strengthIndicator = document.createElement('div');
        strengthIndicator.className = 'password-strength';
        container.appendChild(strengthIndicator);
    }
    
    let strengthBar = strengthIndicator.querySelector('.strength-bar');
    if (!strengthBar) {
        strengthBar = document.createElement('div');
        strengthBar.className = 'strength-bar';
        strengthIndicator.appendChild(strengthBar);
    }
    
    let strengthFill = strengthBar.querySelector('.strength-fill');
    if (!strengthFill) {
        strengthFill = document.createElement('div');
        strengthFill.className = 'strength-fill';
        strengthBar.appendChild(strengthFill);
    }
    
    let strengthText = strengthIndicator.querySelector('.strength-text');
    if (!strengthText) {
        strengthText = document.createElement('div');
        strengthText.className = 'strength-text';
        strengthIndicator.appendChild(strengthText);
    }
    
    const strengths = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const colors = ['#ff6b6b', '#ff9e6b', '#ffd56b', '#6bff6b', '#4cd964'];
    const strengthClasses = ['strength-weak', 'strength-medium', 'strength-strong'];
    
    // Reset classes
    strengthFill.className = 'strength-fill';
    
    if (password.length === 0) {
        strengthText.textContent = 'Enter a password';
        strengthFill.style.width = '0%';
        return;
    }
    
    strengthText.textContent = strengths[strength];
    strengthFill.style.width = `${(strength / 4) * 100}%`;
    
    if (strength <= 1) {
        strengthFill.classList.add('strength-weak');
    } else if (strength <= 2) {
        strengthFill.classList.add('strength-medium');
    } else {
        strengthFill.classList.add('strength-strong');
    }
    
    // Add feedback
    if (feedback.length > 0 && strength < 4) {
        strengthText.textContent += ` - Needs ${feedback.join(', ')}`;
    }
}

function initializeUsernameCheck() {
    const usernameInput = document.getElementById('id_username') || document.querySelector('input[name="username"]');
    if (usernameInput) {
        let checkTimeout;
        
        usernameInput.addEventListener('input', function() {
            clearTimeout(checkTimeout);
            checkTimeout = setTimeout(() => {
                if (this.value.length >= 3) {
                    checkUsernameAvailability(this.value);
                }
            }, 500);
        });
    }
}

function checkUsernameAvailability(username) {
    if (username.length < 3) return;
    
    // Show loading state
    const input = document.getElementById('id_username') || document.querySelector('input[name="username"]');
    input.classList.add('checking');
    
    // Simulate API call (replace with actual API endpoint)
    setTimeout(() => {
        input.classList.remove('checking');
        
        // Mock availability check - replace with actual API call
        const isAvailable = Math.random() > 0.5; // Simulate random availability
        
        if (isAvailable) {
            input.classList.add('success');
            input.classList.remove('error');
            showFieldMessage(input, 'Username is available', 'success');
        } else {
            input.classList.add('error');
            input.classList.remove('success');
            showFieldError(input, 'Username is already taken');
        }
    }, 1000);
    
    // Actual API implementation would look like this:
    /*
    fetch('/api/check-username/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ username: username })
    })
    .then(response => response.json())
    .then(data => {
        input.classList.remove('checking');
        if (data.available) {
            input.classList.add('success');
            showFieldMessage(input, 'Username is available', 'success');
        } else {
            input.classList.add('error');
            showFieldError(input, 'Username is already taken');
        }
    })
    .catch(error => {
        input.classList.remove('checking');
        console.error('Error checking username:', error);
    });
    */
}

function showFieldMessage(field, message, type = 'success') {
    clearFieldError(field);
    
    let messageElement = field.parentNode.querySelector('.form-message');
    if (!messageElement) {
        messageElement = document.createElement('div');
        messageElement.className = `form-message form-message-${type}`;
        field.parentNode.appendChild(messageElement);
    }
    
    messageElement.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${message}`;
    messageElement.style.display = 'block';
    
    // Auto-hide success messages after 3 seconds
    if (type === 'success') {
        setTimeout(() => {
            messageElement.style.display = 'none';
        }, 3000);
    }
}

function initializePasswordToggle() {
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.closest('.input-with-icon').querySelector('input');
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
                this.setAttribute('aria-label', 'Hide password');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
                this.setAttribute('aria-label', 'Show password');
            }
        });
    });
}

function initializeTermsValidation() {
    const termsCheckbox = document.querySelector('#terms');
    const submitButton = document.querySelector('button[type="submit"]');
    
    if (termsCheckbox && submitButton) {
        termsCheckbox.addEventListener('change', function() {
            if (this.checked) {
                submitButton.disabled = false;
            } else {
                submitButton.disabled = true;
            }
        });
        
        // Initial state check
        submitButton.disabled = !termsCheckbox.checked;
    }
}

function initializeSessionManagement() {
    checkAuthStatus();
    
    // Update auth status when auth state changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'class') {
                checkAuthStatus();
            }
        });
    });
    
    observer.observe(document.body, { attributes: true });
}

function checkAuthStatus() {
    const authElements = document.querySelectorAll('[data-auth]');
    const isLoggedIn = document.body.classList.contains('logged-in');
    
    authElements.forEach(element => {
        const requiredAuth = element.getAttribute('data-auth');
        
        if (requiredAuth === 'true' && !isLoggedIn) {
            element.style.display = 'none';
        } else if (requiredAuth === 'false' && isLoggedIn) {
            element.style.display = 'none';
        } else {
            element.style.display = '';
        }
    });
}

function initializeAutoLogout() {
    let inactivityTimer;
    const logoutTime = 30 * 60 * 1000; // 30 minutes
    
    function resetTimer() {
        clearTimeout(inactivityTimer);
        inactivityTimer = setTimeout(logout, logoutTime);
    }
    
    function logout() {
        if (confirm('You will be logged out due to inactivity. Continue?')) {
            resetTimer();
        } else {
            window.location.href = '/logout/';
        }
    }
    
    // Reset timer on user activity
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    events.forEach(event => {
        document.addEventListener(event, resetTimer, true);
    });
    
    resetTimer(); // Start the timer
}

function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.classList.add('loading');
        const originalText = button.textContent;
        button.setAttribute('data-original-text', originalText);
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    } else {
        button.disabled = false;
        button.classList.remove('loading');
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.textContent = originalText;
        }
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    // Remove existing notifications of the same type
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => {
        if (notification.classList.contains(`notification-${type}`)) {
            notification.remove();
        }
    });
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} animate-fadeInUp`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add styles if not already present
    if (!document.querySelector('#notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                min-width: 300px;
                max-width: 500px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                border-left: 4px solid;
                animation: slideInRight 0.3s ease-out;
            }
            .notification-content {
                padding: 1rem;
                display: flex;
                align-items: center;
                gap: 0.8rem;
            }
            .notification-close {
                background: none;
                border: none;
                cursor: pointer;
                margin-left: auto;
                opacity: 0.7;
                transition: opacity 0.3s ease;
            }
            .notification-close:hover {
                opacity: 1;
            }
            .notification-info { border-color: #2196f3; color: #1565c0; }
            .notification-success { border-color: #4caf50; color: #2e7d32; }
            .notification-error { border-color: #f44336; color: #c62828; }
            .notification-warning { border-color: #ff9800; color: #ef6c00; }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideInRight 0.3s ease-out reverse';
            setTimeout(() => notification.remove(), 300);
        }
    }, duration);
    
    return notification;
}

function getNotificationIcon(type) {
    const icons = {
        'info': 'info-circle',
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle'
    };
    return icons[type] || 'info-circle';
}

// CSRF Token function
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Utility function to check if user is logged in
function isLoggedIn() {
    return document.body.classList.contains('logged-in');
}

// Export functions for global access (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeAuthFeatures,
        validateForm,
        showNotification,
        getCSRFToken,
        isLoggedIn
    };
}