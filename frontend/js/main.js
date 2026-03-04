// Image Slider Functionality
let currentSlide = 0;
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');

function showSlide(n) {
    // Remove active class from all slides and dots
    slides.forEach(slide => slide.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));
    
    // Handle wraparound
    currentSlide = (n + slides.length) % slides.length;
    
    // Add active class to current slide and dot
    slides[currentSlide].classList.add('active');
    if (dots[currentSlide]) {
        dots[currentSlide].classList.add('active');
    }
}

function changeSlide(direction) {
    showSlide(currentSlide + direction);
}

function currentSlide(n) {
    showSlide(n - 1);
}

// Auto-advance slides every 5 seconds
let slideInterval = setInterval(() => {
    changeSlide(1);
}, 5000);

// Pause auto-advance on hover
const slider = document.querySelector('.slider');
if (slider) {
    slider.addEventListener('mouseenter', () => {
        clearInterval(slideInterval);
    });

    slider.addEventListener('mouseleave', () => {
        slideInterval = setInterval(() => {
            changeSlide(1);
        }, 5000);
    });
}

// Mobile Menu Toggle
const navMenu = document.querySelector('.nav-menu');
if (navMenu) {
    navMenu.querySelectorAll('li').forEach(item => {
        item.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                const dropdown = item.querySelector('.dropdown');
                if (dropdown) {
                    e.preventDefault();
                    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
                }
            }
        });
    });
}

// Smooth Scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#' && document.querySelector(href)) {
            e.preventDefault();
            document.querySelector(href).scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Disabled Link Alert
document.querySelectorAll('.disabled-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        alert('This feature requires member login. Please register or login to access this section.');
    });
});

// Stats Counter Animation (when in viewport)
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    function updateCounter() {
        start += increment;
        if (start < target) {
            element.textContent = Math.floor(start) + '+';
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target + '+';
        }
    }
    
    updateCounter();
}

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.5,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
            
            // Animate stat numbers when they come into view
            if (entry.target.classList.contains('stat-number')) {
                const text = entry.target.textContent;
                const number = parseInt(text.replace(/\D/g, ''));
                if (!isNaN(number)) {
                    animateCounter(entry.target, number);
                }
            }
            
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements for animation
document.querySelectorAll('.vm-card, .news-card, .event-card, .stat-card').forEach(card => {
    observer.observe(card);
});

// Form Validation (for future forms)
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}

// Dynamic content loading placeholder
// This will be replaced with actual API calls in Phase 2
const contentAPI = {
    // Placeholder for future API endpoints
    baseURL: '/api',
    
    // Get announcements
    getAnnouncements: async function() {
        // TODO: Replace with actual API call in Phase 2
        return [
            {
                date: 'February 20, 2026',
                title: 'Website Launch Announcement',
                content: 'We are thrilled to announce the launch of our official alumni website!',
                link: '#'
            }
        ];
    },
    
    // Get events
    getEvents: async function() {
        // TODO: Replace with actual API call in Phase 2
        return [];
    },
    
    // Get slider images
    getSliderImages: async function() {
        // TODO: Replace with actual API call in Phase 2
        return [];
    }
};

// Add CSS animation class
const style = document.createElement('style');
style.textContent = `
    .animate-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);

// Console welcome message
console.log('%c🎓 JU 18th Batch Alumni Association', 'color: #1e3c72; font-size: 20px; font-weight: bold;');
console.log('%cWebsite Version 1.0 - Phase 1: Static Frontend', 'color: #666; font-size: 14px;');
console.log('%cDeveloped for Jahangirnagar University 18th Batch', 'color: #666; font-size: 12px;');

// Keyboard navigation for slider
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') {
        changeSlide(-1);
    } else if (e.key === 'ArrowRight') {
        changeSlide(1);
    }
});

// Print debug info
console.log('Frontend initialized successfully');
console.log(`Total slides: ${slides.length}`);
console.log(`Current slide: ${currentSlide + 1}`);
