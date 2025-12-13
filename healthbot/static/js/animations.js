// Animation and interactive effects
document.addEventListener('DOMContentLoaded', function() {
    // Scroll animations
    const revealElements = document.querySelectorAll('.reveal');
    
    const revealOnScroll = function() {
        revealElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                element.classList.add('active');
            }
        });
    };
    
    window.addEventListener('scroll', revealOnScroll);
    revealOnScroll(); // Initial check
    
    // Parallax effect for hero section
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            heroSection.style.transform = `translateY(${rate}px)`;
        });
    }
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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
    
    // Typing effect for hero title
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        let i = 0;
        
        function typeWriter() {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        }
        typeWriter();
    }
    
    // Interactive game cards
    const gameCards = document.querySelectorAll('.game-card');
    gameCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
            this.style.boxShadow = '0 20px 40px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 10px 30px rgba(0,0,0,0.1)';
        });
    });
    
    // Floating action button
    const createFAB = function() {
        const fab = document.createElement('button');
        fab.className = 'fab';
        fab.innerHTML = '<i class="fas fa-arrow-up"></i>';
        fab.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        document.body.appendChild(fab);
        
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                fab.style.opacity = '1';
                fab.style.transform = 'scale(1)';
            } else {
                fab.style.opacity = '0';
                fab.style.transform = 'scale(0)';
            }
        });
    };
    createFAB();
    
    // Health stats counter animation
    const animateCounters = function() {
        const counters = document.querySelectorAll('.stat h3');
        counters.forEach(counter => {
            const target = parseInt(counter.textContent);
            let count = 0;
            const increment = target / 100;
            
            const updateCount = function() {
                if (count < target) {
                    count += increment;
                    counter.textContent = Math.ceil(count) + '+';
                    setTimeout(updateCount, 20);
                } else {
                    counter.textContent = target + '+';
                }
            };
            updateCount();
        });
    };
    
    // Intersection Observer for counter animation
    const statsSection = document.querySelector('.hero-stats');
    if (statsSection) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounters();
                    observer.unobserve(entry.target);
                }
            });
        });
        observer.observe(statsSection);
    }
    
    // Chat message animations
    const observeChatMessages = function() {
        const chatWindow = document.getElementById('chat-window');
        if (chatWindow) {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1) { // Element node
                            node.style.animation = 'fadeInUp 0.5s ease-out';
                        }
                    });
                });
            });
            
            observer.observe(chatWindow, { childList: true });
        }
    };
    observeChatMessages();
    
    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobile-menu');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            mobileMenuToggle.classList.toggle('active');
        });
    }
    
    // Language switch animation
    const languageSelect = document.getElementById('language');
    if (languageSelect) {
        languageSelect.addEventListener('change', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    }
    
    // Loading animations for images
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('load', function() {
            this.style.animation = 'fadeIn 0.5s ease-out';
        });
    });
    
    // Pulse animation for important elements
    const importantElements = document.querySelectorAll('.important, .cta-button');
    importantElements.forEach(el => {
        setInterval(() => {
            el.classList.toggle('pulse');
        }, 2000);
    });
});

// Utility function for random animations
function getRandomAnimation() {
    const animations = [
        'animate-fadeIn', 'animate-fadeInUp', 'animate-fadeInLeft', 'animate-fadeInRight',
        'animate-bounceIn', 'animate-rotate', 'animate-float'
    ];
    return animations[Math.floor(Math.random() * animations.length)];
}

// Add random animations to elements
function addRandomAnimations() {
    const elements = document.querySelectorAll('');
    elements.forEach(el => {
        el.classList.add(getRandomAnimation());
    });
}

// Initialize when page loads
window.addEventListener('load', function() {
    addRandomAnimations();
});