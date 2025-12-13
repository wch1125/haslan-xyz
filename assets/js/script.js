// ============================================
// GWERN-INSPIRED JAVASCRIPT FEATURES
// Enhanced for H. Aslan Wiki
// ============================================

// ============================================
// Auto-Enhancement System
// Automatically applies typography and linking
// ============================================
const AutoEnhance = {
    definitions: {},
    
    async init() {
        await this.loadDefinitions();
        this.applyDropcaps();
        this.linkDefinitions();
        this.enhanceWritingContent();
        
        // Re-attach popup listeners for newly created definition links
        if (typeof LinkPopup !== 'undefined' && LinkPopup.attachDefinitionListeners) {
            LinkPopup.attachDefinitionListeners();
        }
    },
    
    // Load definitions from the definitions page
    async loadDefinitions() {
        try {
            // Determine the path to definitions.html based on current location
            const currentPath = window.location.pathname;
            let definitionsPath;
            
            if (currentPath.includes('/pages/writing/')) {
                definitionsPath = '../definitions.html';
            } else if (currentPath.includes('/pages/')) {
                definitionsPath = 'definitions.html';
            } else {
                definitionsPath = 'pages/definitions.html';
            }
            
            const response = await fetch(definitionsPath);
            if (!response.ok) return;
            
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Extract definitions
            doc.querySelectorAll('.definition-entry').forEach(entry => {
                const termEl = entry.querySelector('.definition-term');
                const contentEl = entry.querySelector('.definition-content p');
                const id = entry.getAttribute('id');
                
                if (termEl && contentEl && id) {
                    const term = termEl.textContent.trim();
                    // Get first ~150 chars of definition for preview
                    let preview = contentEl.textContent.trim();
                    if (preview.length > 150) {
                        preview = preview.substring(0, 147) + '...';
                    }
                    
                    this.definitions[term.toLowerCase()] = {
                        term: term,
                        slug: id,
                        preview: preview
                    };
                }
            });
        } catch (e) {
            // Silently fail - definitions just won't auto-link
            console.log('Could not load definitions for auto-linking');
        }
    },
    
    // Auto-apply dropcaps to first paragraph of content sections
    applyDropcaps() {
        // Target first paragraph in main content areas
        const selectors = [
            'section#introduction > p:first-of-type',
            '.writing-content > p:first-of-type',
            'article > section:first-of-type > p:first-of-type'
        ];
        
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(p => {
                // Skip if already has a dropcap
                if (p.querySelector('.dropcap')) return;
                // Skip if paragraph is too short
                if (p.textContent.trim().length < 50) return;
                
                const text = p.innerHTML;
                // Find the first actual letter (skip any HTML tags at start)
                const match = text.match(/^(\s*(?:<[^>]+>)*)([A-Za-z])/);
                if (match) {
                    const before = match[1] || '';
                    const letter = match[2];
                    const after = text.substring(match[0].length);
                    p.innerHTML = `${before}<span class="dropcap">${letter}</span>${after}`;
                }
            });
        });
    },
    
    // Auto-link defined terms in content
    linkDefinitions() {
        if (Object.keys(this.definitions).length === 0) return;
        
        // Don't process the definitions page itself
        if (window.location.pathname.includes('definitions.html')) return;
        
        // Get the correct path prefix for links
        const currentPath = window.location.pathname;
        let linkPrefix;
        if (currentPath.includes('/pages/writing/')) {
            linkPrefix = '../definitions.html';
        } else if (currentPath.includes('/pages/')) {
            linkPrefix = 'definitions.html';
        } else {
            linkPrefix = 'pages/definitions.html';
        }
        
        // Content areas to process
        const contentAreas = document.querySelectorAll(
            'article p, article li, .writing-content, .abstract p, blockquote'
        );
        
        contentAreas.forEach(el => {
            // Skip if inside a link or heading
            if (el.closest('a') || el.closest('h1, h2, h3, h4')) return;
            
            this.processTextNode(el, linkPrefix);
        });
    },
    
    processTextNode(element, linkPrefix) {
        // Get all text nodes in this element
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            // Skip if parent is already a link or definition-link
            if (node.parentElement.closest('a, .definition-link')) continue;
            textNodes.push(node);
        }
        
        // Process each text node
        textNodes.forEach(textNode => {
            let html = textNode.textContent;
            let modified = false;
            
            // Check each definition term
            for (const [termLower, def] of Object.entries(this.definitions)) {
                // Match whole words only, case-insensitive but preserve original case
                // Match the term with a capital first letter (as Defined Terms should appear)
                const capitalizedTerm = def.term;
                const regex = new RegExp(`\\b(${this.escapeRegex(capitalizedTerm)})\\b`, 'g');
                
                if (regex.test(html)) {
                    modified = true;
                    html = html.replace(regex, 
                        `<a href="${linkPrefix}#${def.slug}" class="definition-link" data-term="${def.term}" data-definition="${this.escapeHtml(def.preview)}">$1</a>`
                    );
                }
            }
            
            if (modified) {
                const span = document.createElement('span');
                span.innerHTML = html;
                textNode.parentNode.replaceChild(span, textNode);
            }
        });
    },
    
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    },
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/"/g, '&quot;');
    },
    
    // Enhance writing content with additional formatting
    enhanceWritingContent() {
        // Auto-format poetry/verse (lines ending without periods)
        document.querySelectorAll('.writing-content').forEach(content => {
            // Add verse class if content looks like poetry
            const text = content.textContent;
            const lines = text.split('\n').filter(l => l.trim());
            const shortLines = lines.filter(l => l.trim().length < 60 && !l.trim().endsWith('.')); 
            
            if (shortLines.length > lines.length * 0.5) {
                content.classList.add('verse');
            }
        });
    }
};

// Initialize auto-enhancement after DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    AutoEnhance.init();
});

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
        document.querySelectorAll('a[href^="pages/"], a[href$=".html"]:not([href^="http"])').forEach(link => {
            // Skip definition links - they have their own handler
            if (link.classList.contains('definition-link')) return;
            link.addEventListener('mouseenter', (e) => this.showPagePreview(e));
            link.addEventListener('mouseleave', () => this.hide());
        });

        // Initial attachment for definition links
        this.attachDefinitionListeners();
    },
    
    // Separate method so it can be called after auto-enhancement
    attachDefinitionListeners() {
        document.querySelectorAll('a.definition-link').forEach(link => {
            // Avoid duplicate listeners
            if (link.dataset.popupAttached) return;
            link.dataset.popupAttached = 'true';
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
// Quote Filter System (Dynamic)
// ============================================
const QuoteFilter = {
    init() {
        const container = document.getElementById('filter-buttons');
        const quotes = document.querySelectorAll('.quote-entry');
        
        if (!container || quotes.length === 0) return;
        
        // Collect all unique tags from quotes
        const allTags = new Set();
        quotes.forEach(quote => {
            const tags = quote.getAttribute('data-tags');
            if (tags) {
                tags.split(',').forEach(tag => {
                    const trimmed = tag.trim().toLowerCase();
                    if (trimmed) allTags.add(trimmed);
                });
            }
        });
        
        // Sort tags alphabetically
        const sortedTags = Array.from(allTags).sort();
        
        // Build filter buttons
        container.innerHTML = '';
        
        // "All" button first
        const allBtn = document.createElement('button');
        allBtn.className = 'filter-btn active';
        allBtn.setAttribute('data-filter', 'all');
        allBtn.textContent = 'All';
        container.appendChild(allBtn);
        
        // Tag buttons
        sortedTags.forEach(tag => {
            const btn = document.createElement('button');
            btn.className = 'filter-btn';
            btn.setAttribute('data-filter', tag);
            // Capitalize first letter for display
            btn.textContent = tag.charAt(0).toUpperCase() + tag.slice(1);
            container.appendChild(btn);
        });
        
        // Attach click handlers
        const filterButtons = container.querySelectorAll('.filter-btn');
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                const filter = button.getAttribute('data-filter');
                
                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Filter quotes
                quotes.forEach(quote => {
                    const tags = quote.getAttribute('data-tags').toLowerCase().split(',').map(t => t.trim());
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

// ============================================
// Definition Alphabetical Index (Dynamic)
// ============================================
const DefinitionIndex = {
    init() {
        const container = document.getElementById('alpha-index');
        const definitions = document.querySelectorAll('.definition-entry');
        
        if (!container || definitions.length === 0) return;
        
        // Collect unique first letters from definition terms
        const letters = new Set();
        definitions.forEach(def => {
            const letterSpan = def.querySelector('.definition-letter');
            if (letterSpan) {
                letters.add(letterSpan.textContent.trim().toUpperCase());
            }
        });
        
        // Sort alphabetically
        const sortedLetters = Array.from(letters).sort();
        
        // Build index links
        container.innerHTML = '';
        sortedLetters.forEach(letter => {
            const link = document.createElement('a');
            link.href = '#' + letter;
            link.textContent = letter;
            container.appendChild(link);
            
            // Add letter anchor to first definition starting with that letter
            definitions.forEach(def => {
                const letterSpan = def.querySelector('.definition-letter');
                if (letterSpan && letterSpan.textContent.trim().toUpperCase() === letter) {
                    // Check if anchor doesn't already exist
                    if (!document.getElementById(letter)) {
                        def.setAttribute('id', def.getAttribute('id')); // Keep existing ID
                        // Add a named anchor before this definition
                        const anchor = document.createElement('a');
                        anchor.setAttribute('name', letter);
                        anchor.id = letter;
                        def.parentNode.insertBefore(anchor, def);
                    }
                }
            });
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    DefinitionIndex.init();
});

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
