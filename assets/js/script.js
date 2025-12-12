// ============================================
// GWERN-INSPIRED JAVASCRIPT FEATURES
// Enhanced for H. Aslan Wiki
// ============================================

// ============================================
// Dark Mode Toggle
// ============================================
const themeToggle = document.getElementById('theme-toggle-btn');
const htmlElement = document.documentElement;

// Load saved theme or default to light
const savedTheme = localStorage.getItem('theme') || 'light';
htmlElement.setAttribute('data-theme', savedTheme);

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

// ============================================
// Active Navigation Highlighting
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-section a');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPath.includes(href) && href !== 'index.html') {
            link.style.color = 'var(--link-color)';
            link.style.fontWeight = '600';
        }
    });
});

// ============================================
// Link Popup Previews (Enhanced)
// ============================================
const LinkPopup = {
    popup: null,
    timeout: null,
    currentLink: null,
    definitionsCache: {},
    
    // Page excerpts for internal links
    excerpts: {
        'pages/creative-writing.html': {
            title: 'Creative Writing',
            text: 'Short stories, poems, passages, and experiments. Fiction as a way of thinking through problems that analysis can\'t quite reach.'
        },
        'pages/quotes.html': {
            title: 'Quotes',
            text: 'A collection of quotes that have shaped thinking. Organized chronologically with tags for filtering by author, work, and theme.'
        },
        'pages/definitions.html': {
            title: 'Definitions',
            text: 'A glossary of Defined Terms used throughout the site. Hover over capitalized terms to see their definitions.'
        },
        'pages/credit-agreement.html': {
            title: 'The HTML Credit Agreement',
            text: 'A novel in progress, structured as a credit agreement with chapters organized as contract sections.'
        },
        'pages/contact.html': {
            title: 'Contact',
            text: 'Get in touch regarding commission work or general inquiries.'
        }
    },
    
    init() {
        // Only enable on desktop with hover capability
        if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
            return;
        }
        
        // Create popup element
        this.popup = document.createElement('div');
        this.popup.className = 'link-popup';
        document.body.appendChild(this.popup);
        
        // Attach event listeners to all internal page links
        document.querySelectorAll('a[href^="pages/"]').forEach(link => {
            link.addEventListener('mouseenter', (e) => this.showPagePreview(e));
            link.addEventListener('mouseleave', () => this.hide());
        });

        // Attach event listeners to definition links
        document.querySelectorAll('a.definition-link').forEach(link => {
            link.addEventListener('mouseenter', (e) => this.showDefinition(e));
            link.addEventListener('mouseleave', () => this.hide());
        });
    },
    
    showPagePreview(event) {
        clearTimeout(this.timeout);
        
        const link = event.target.closest('a');
        const href = link.getAttribute('href');
        const excerpt = this.excerpts[href];
        
        if (!excerpt) return;
        
        this.currentLink = link;
        
        // Delay popup slightly for better UX
        this.timeout = setTimeout(() => {
            this.popup.innerHTML = `
                <div class="link-popup-title">${excerpt.title}</div>
                <div class="link-popup-excerpt">${excerpt.text}</div>
            `;
            
            this.positionPopup(link);
            this.popup.classList.add('show');
        }, 300);
    },

    showDefinition(event) {
        clearTimeout(this.timeout);
        
        const link = event.target.closest('a');
        const term = link.getAttribute('data-term');
        const definition = link.getAttribute('data-definition');
        
        if (!definition) return;
        
        this.currentLink = link;
        
        this.timeout = setTimeout(() => {
            this.popup.innerHTML = `
                <div class="link-popup-title">${term}</div>
                <div class="link-popup-excerpt">${definition}</div>
            `;
            
            this.positionPopup(link);
            this.popup.classList.add('show');
        }, 200);
    },

    positionPopup(link) {
        const linkRect = link.getBoundingClientRect();
        const popupRect = this.popup.getBoundingClientRect();
        
        let top = linkRect.bottom + window.scrollY + 10;
        let left = linkRect.left + window.scrollX;
        
        // Keep popup on screen horizontally
        if (left + 400 > window.innerWidth) {
            left = window.innerWidth - 420;
        }
        if (left < 20) {
            left = 20;
        }
        
        // Keep popup on screen vertically
        if (top + popupRect.height > window.innerHeight + window.scrollY) {
            top = linkRect.top + window.scrollY - popupRect.height - 10;
        }
        
        this.popup.style.top = top + 'px';
        this.popup.style.left = left + 'px';
    },
    
    hide() {
        clearTimeout(this.timeout);
        this.popup.classList.remove('show');
        this.currentLink = null;
    }
};

// Initialize link popups when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    LinkPopup.init();
});

// ============================================
// Smooth Scroll for Anchor Links
// ============================================
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

// ============================================
// Sidenote Mobile Conversion
// ============================================
function setupSidenotes() {
    if (window.innerWidth <= 1100) {
        document.querySelectorAll('.sidenote').forEach(sidenote => {
            const content = sidenote.querySelector('.sidenote-content');
            if (content) {
                sidenote.setAttribute('data-sidenote', content.textContent);
            }
        });
    }
}

window.addEventListener('load', setupSidenotes);
window.addEventListener('resize', setupSidenotes);

// ============================================
// Keyboard Shortcuts
// ============================================
document.addEventListener('keydown', function(e) {
    // Alt+D: Toggle dark mode
    if (e.altKey && e.key === 'd') {
        e.preventDefault();
        if (themeToggle) themeToggle.click();
    }
    
    // Alt+H: Go to home
    if (e.altKey && e.key === 'h') {
        e.preventDefault();
        window.location.href = '/index.html';
    }
});

// ============================================
// External Link Handling
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="http"]');
    links.forEach(link => {
        // Skip if it's an internal link or has an image
        if (link.querySelector('img')) return;
        if (link.href.includes(window.location.hostname)) return;
        
        // Add external link attributes
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
    });
});

// ============================================
// Collapse Section State Persistence
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const details = document.querySelectorAll('details');
    
    details.forEach((detail, index) => {
        const key = `collapse-${index}-${window.location.pathname}`;
        
        // Restore state
        const saved = localStorage.getItem(key);
        if (saved === 'open') {
            detail.open = true;
        }
        
        // Save state on toggle
        detail.addEventListener('toggle', function() {
            localStorage.setItem(key, this.open ? 'open' : 'closed');
        });
    });
});

// ============================================
// Search Functionality (for future use)
// ============================================
const SiteSearch = {
    index: null,
    
    init() {
        const searchInput = document.getElementById('site-search');
        if (!searchInput) return;
        
        searchInput.addEventListener('input', this.handleSearch.bind(this));
    },
    
    handleSearch(event) {
        const query = event.target.value.toLowerCase();
        if (query.length < 2) return;
        
        // Simple search implementation
        // In a production site, you'd want to use something like Lunr.js
        console.log('Searching for:', query);
    }
};

// ============================================
// Table of Contents Generator
// ============================================
const TOC = {
    generate() {
        const article = document.querySelector('article');
        const tocContainer = document.getElementById('table-of-contents');
        
        if (!article || !tocContainer) return;
        
        const headings = article.querySelectorAll('h2, h3');
        if (headings.length === 0) return;
        
        const toc = document.createElement('ul');
        toc.className = 'toc-list';
        
        headings.forEach((heading, index) => {
            // Add ID if it doesn't have one
            if (!heading.id) {
                heading.id = `section-${index}`;
            }
            
            const li = document.createElement('li');
            li.className = heading.tagName.toLowerCase();
            
            const link = document.createElement('a');
            link.href = `#${heading.id}`;
            link.textContent = heading.textContent;
            
            li.appendChild(link);
            toc.appendChild(li);
        });
        
        tocContainer.appendChild(toc);
    }
};

// ============================================
// Performance: Lazy Load Images
// ============================================
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });
    
    document.querySelectorAll('img.lazy').forEach(img => {
        imageObserver.observe(img);
    });
}

// ============================================
// Quote Filter System
// ============================================
const QuoteFilter = {
    init() {
        const filterButtons = document.querySelectorAll('.filter-btn');
        const quotes = document.querySelectorAll('.quote-entry');
        
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                const filter = button.getAttribute('data-filter');
                
                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Filter quotes
                quotes.forEach(quote => {
                    const tags = quote.getAttribute('data-tags').split(',');
                    if (filter === 'all' || tags.includes(filter)) {
                        quote.style.display = 'block';
                    } else {
                        quote.style.display = 'none';
                    }
                });
            });
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    QuoteFilter.init();
});

// ============================================
// Console Easter Egg
// ============================================
console.log('%cH. Aslan', 'font-size: 24px; font-weight: bold; font-style: italic;');
console.log('%c"Not a tame lion."', 'font-size: 12px; color: #666; font-style: italic;');
console.log('%cKeyboard shortcuts: Alt+D (dark mode), Alt+H (home)', 'font-size: 11px;');

// ============================================
// Utility Functions
// ============================================
const Utils = {
    // Debounce function for performance
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Format date
    formatDate(date) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(date).toLocaleDateString('en-US', options);
    },
    
    // Get reading time
    getReadingTime(text) {
        const wordsPerMinute = 200;
        const words = text.trim().split(/\s+/).length;
        const minutes = Math.ceil(words / wordsPerMinute);
        return `${minutes} min read`;
    }
};
