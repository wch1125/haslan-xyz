// ============================================
// H. ASLAN WIKI - ENHANCED JAVASCRIPT
// "Not a tame lion."
// Premium interactions and subtle lion motifs
// ============================================

(function() {
    'use strict';

    // ============================================
    // LOADING SCREEN (Conditional)
    // Only shows on first visit per session
    // Respects prefers-reduced-motion
    // ============================================
    
    const LoadingScreen = {
        init() {
            const loadingScreen = document.getElementById('loading-screen');
            if (!loadingScreen) return;
            
            // Check if user prefers reduced motion
            const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            
            // Check if already shown this session
            const hasSeenLoading = sessionStorage.getItem('wiki-loading-seen');
            
            // Skip loading screen if reduced motion or already seen
            if (prefersReducedMotion || hasSeenLoading) {
                loadingScreen.classList.add('hidden');
                loadingScreen.style.display = 'none';
                return;
            }
            
            // Mark as seen for this session
            sessionStorage.setItem('wiki-loading-seen', 'true');
            
            // Add skip button functionality
            const skipBtn = loadingScreen.querySelector('.loading-skip');
            if (skipBtn) {
                skipBtn.addEventListener('click', () => this.hide());
            }
            
            // Also allow clicking anywhere or pressing any key to skip
            loadingScreen.addEventListener('click', () => this.hide());
            document.addEventListener('keydown', () => this.hide(), { once: true });
            
            // Auto-hide after animation completes
            setTimeout(() => this.hide(), 1200);
        },
        
        hide() {
            const loadingScreen = document.getElementById('loading-screen');
            if (loadingScreen && !loadingScreen.classList.contains('hidden')) {
                loadingScreen.classList.add('hidden');
            }
        }
    };

    // ============================================
    // READING PROGRESS BAR
    // ============================================
    
    const ReadingProgress = {
        progressBar: null,
        progressContainer: null,
        
        init() {
            // Create progress bar elements
            this.progressContainer = document.createElement('div');
            this.progressContainer.className = 'reading-progress';
            
            this.progressBar = document.createElement('div');
            this.progressBar.className = 'reading-progress-bar';
            
            this.progressContainer.appendChild(this.progressBar);
            document.body.appendChild(this.progressContainer);
            
            // Throttled scroll handler
            let ticking = false;
            window.addEventListener('scroll', () => {
                if (!ticking) {
                    requestAnimationFrame(() => {
                        this.update();
                        ticking = false;
                    });
                    ticking = true;
                }
            });
            
            this.update();
        },
        
        update() {
            const scrollTop = window.scrollY;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
            
            this.progressBar.style.width = `${progress}%`;
            
            // Show/hide based on scroll position
            if (scrollTop > 100) {
                this.progressContainer.classList.add('visible');
            } else {
                this.progressContainer.classList.remove('visible');
            }
        }
    };

    // ============================================
    // SCROLL REVEAL ANIMATIONS
    // ============================================
    
    const ScrollReveal = {
        init() {
            // Respect reduced motion preference
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
            if (!('IntersectionObserver' in window)) return;
            
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('revealed');
                    }
                });
            }, observerOptions);
            
            // Add reveal class to elements and observe
            const revealSelectors = [
                '.topic-card',
                '.definition-entry',
                '.quote-entry',
                '.writing-card',
                'section > h2',
                '.abstract',
                '.start-here-card'
            ];
            
            document.querySelectorAll(revealSelectors.join(', ')).forEach(el => {
                if (!el.classList.contains('reveal')) {
                    el.classList.add('reveal');
                }
                observer.observe(el);
            });
            
            // Stagger animations for grids
            document.querySelectorAll('.topic-grid, .start-here-grid').forEach(grid => {
                grid.classList.add('reveal-stagger');
                observer.observe(grid);
            });
        }
    };

    // ============================================
    // AUTO-ENHANCEMENT SYSTEM
    // Definitions, dropcaps, and more
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
        
        async loadDefinitions() {
            try {
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
                
                doc.querySelectorAll('.definition-entry').forEach(entry => {
                    const termEl = entry.querySelector('.definition-term');
                    const contentEl = entry.querySelector('.definition-content p');
                    const id = entry.getAttribute('id');
                    
                    if (termEl && contentEl && id) {
                        const term = termEl.textContent.trim();
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
                console.log('Could not load definitions for auto-linking');
            }
        },
        
        applyDropcaps() {
            const selectors = [
                'section#introduction > p:first-of-type',
                'section#intro > p:first-of-type',
                '.writing-content > p:first-of-type',
                'article > section:first-of-type > p:first-of-type'
            ];
            
            selectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(p => {
                    if (p.querySelector('.dropcap')) return;
                    if (p.textContent.trim().length < 50) return;
                    
                    const text = p.innerHTML;
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
        
        linkDefinitions() {
            if (Object.keys(this.definitions).length === 0) return;
            if (window.location.pathname.includes('definitions.html')) return;
            
            const currentPath = window.location.pathname;
            let linkPrefix;
            if (currentPath.includes('/pages/writing/')) {
                linkPrefix = '../definitions.html';
            } else if (currentPath.includes('/pages/')) {
                linkPrefix = 'definitions.html';
            } else {
                linkPrefix = 'pages/definitions.html';
            }
            
            const contentAreas = document.querySelectorAll(
                'article p, article li, .writing-content, .abstract p, blockquote'
            );
            
            contentAreas.forEach(el => {
                if (el.closest('a') || el.closest('h1, h2, h3, h4')) return;
                this.processTextNode(el, linkPrefix);
            });
        },
        
        processTextNode(element, linkPrefix) {
            const walker = document.createTreeWalker(
                element,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );
            
            const textNodes = [];
            let node;
            while (node = walker.nextNode()) {
                if (node.parentElement.closest('a, .definition-link')) continue;
                textNodes.push(node);
            }
            
            textNodes.forEach(textNode => {
                let html = textNode.textContent;
                let modified = false;
                
                for (const [termLower, def] of Object.entries(this.definitions)) {
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
        
        enhanceWritingContent() {
            document.querySelectorAll('.writing-content').forEach(content => {
                const text = content.textContent;
                const lines = text.split('\n').filter(l => l.trim());
                const shortLines = lines.filter(l => l.trim().length < 60 && !l.trim().endsWith('.')); 
                
                if (shortLines.length > lines.length * 0.5) {
                    content.classList.add('verse');
                }
            });
        }
    };

    // ============================================
    // DARK MODE TOGGLE
    // ============================================
    
    const DarkMode = {
        init() {
            const themeToggle = document.getElementById('theme-toggle-btn');
            const htmlElement = document.documentElement;
            
            if (!themeToggle) return;
            
            // Load saved theme or default to system preference
            const savedTheme = localStorage.getItem('wiki-theme');
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            if (savedTheme) {
                htmlElement.setAttribute('data-theme', savedTheme);
            } else if (systemPrefersDark) {
                htmlElement.setAttribute('data-theme', 'dark');
            } else {
                htmlElement.setAttribute('data-theme', 'light');
            }
            
            themeToggle.addEventListener('click', () => {
                const currentTheme = htmlElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                htmlElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('wiki-theme', newTheme);
            });
            
            // Listen for system preference changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('wiki-theme')) {
                    htmlElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
                }
            });
        }
    };

    // ============================================
    // ENHANCED LINK POPUP (with Mobile Support)
    // ============================================
    
    const LinkPopup = {
        popup: null,
        timeout: null,
        activeLink: null,
        isTouchDevice: false,
        
        init() {
            // Detect touch capability
            this.isTouchDevice = ('ontouchstart' in window) || 
                                 (navigator.maxTouchPoints > 0) ||
                                 (navigator.msMaxTouchPoints > 0);
            
            this.createPopup();
            this.attachDefinitionListeners();
            
            // Close popup when tapping elsewhere on mobile
            if (this.isTouchDevice) {
                document.addEventListener('touchstart', (e) => {
                    if (!e.target.closest('.link-popup') && !e.target.closest('.definition-link')) {
                        this.hide();
                        this.activeLink = null;
                    }
                });
            }
        },
        
        createPopup() {
            this.popup = document.createElement('div');
            this.popup.className = 'link-popup';
            this.popup.innerHTML = `
                <div class="link-popup-title"></div>
                <div class="link-popup-excerpt"></div>
                <div class="link-popup-actions">
                    <a class="link-popup-goto" href="#">Go to definition →</a>
                    <button class="link-popup-close" aria-label="Close">✕</button>
                </div>
            `;
            document.body.appendChild(this.popup);
            
            // Handle "Go to definition" click
            this.popup.querySelector('.link-popup-goto').addEventListener('click', (e) => {
                if (this.activeLink) {
                    window.location.href = this.activeLink.href;
                }
            });
            
            // Handle close button
            this.popup.querySelector('.link-popup-close').addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.hide();
                this.activeLink = null;
            });
        },
        
        attachDefinitionListeners() {
            document.querySelectorAll('a.definition-link').forEach(link => {
                // Desktop: hover behavior
                link.addEventListener('mouseenter', (e) => {
                    if (!this.isTouchDevice) {
                        this.show(e);
                    }
                });
                link.addEventListener('mouseleave', () => {
                    if (!this.isTouchDevice) {
                        this.hide();
                    }
                });
                
                // Keyboard accessibility
                link.addEventListener('focus', (e) => this.show(e));
                link.addEventListener('blur', () => this.hide());
                
                // Mobile: tap behavior
                link.addEventListener('click', (e) => {
                    if (this.isTouchDevice) {
                        // First tap: show popup, prevent navigation
                        // Second tap on same link: navigate
                        if (this.activeLink === link && this.popup.classList.contains('show')) {
                            // Second tap - allow navigation
                            return;
                        }
                        
                        e.preventDefault();
                        this.activeLink = link;
                        this.show(e);
                    }
                });
            });
        },
        
        show(e) {
            clearTimeout(this.timeout);
            
            const link = e.target.closest('.definition-link') || e.target;
            const term = link.dataset.term;
            const definition = link.dataset.definition;
            
            if (!term || !definition) return;
            
            this.popup.querySelector('.link-popup-title').textContent = term;
            this.popup.querySelector('.link-popup-excerpt').textContent = definition;
            this.popup.querySelector('.link-popup-goto').href = link.href;
            
            // Position popup
            const rect = link.getBoundingClientRect();
            const popupHeight = this.isTouchDevice ? 160 : 120;
            const spaceAbove = rect.top;
            const spaceBelow = window.innerHeight - rect.bottom;
            
            let top, left;
            
            if (spaceBelow >= popupHeight || spaceBelow >= spaceAbove) {
                top = rect.bottom + window.scrollY + 8;
            } else {
                top = rect.top + window.scrollY - popupHeight - 8;
            }
            
            // On mobile, center the popup horizontally for better readability
            if (this.isTouchDevice) {
                const popupWidth = Math.min(window.innerWidth - 32, 400);
                left = Math.max(16, (window.innerWidth - popupWidth) / 2);
            } else {
                left = Math.max(16, Math.min(
                    rect.left + window.scrollX,
                    window.innerWidth - 420
                ));
            }
            
            this.popup.style.top = `${top}px`;
            this.popup.style.left = `${left}px`;
            
            // Show faster on mobile since user explicitly tapped
            const delay = this.isTouchDevice ? 0 : 100;
            this.timeout = setTimeout(() => {
                this.popup.classList.add('show');
            }, delay);
        },
        
        hide() {
            clearTimeout(this.timeout);
            this.popup.classList.remove('show');
        }
    };

    // ============================================
    // DESKTOP SIDENOTES
    // Positions sidenotes in right margin on hover
    // ============================================
    
    const DesktopSidenotes = {
        init() {
            // Only activate on wider screens
            const mql = window.matchMedia('(min-width: 1101px)');
            
            if (mql.matches) {
                this.setup();
            }
            
            mql.addEventListener('change', (e) => {
                if (e.matches) {
                    this.setup();
                } else {
                    this.teardown();
                }
            });
        },
        
        setup() {
            document.querySelectorAll('.sidenote').forEach(sidenote => {
                const content = sidenote.querySelector('.sidenote-content');
                const number = sidenote.querySelector('.sidenote-number');
                if (!content) return;
                
                // Show on hover/focus
                const showSidenote = () => {
                    this.positionSidenote(sidenote, content);
                    content.classList.add('visible');
                };
                
                const hideSidenote = () => {
                    content.classList.remove('visible');
                };
                
                sidenote.addEventListener('mouseenter', showSidenote);
                sidenote.addEventListener('mouseleave', hideSidenote);
                if (number) {
                    number.addEventListener('focus', showSidenote);
                    number.addEventListener('blur', hideSidenote);
                }
                
                // Store handlers for cleanup
                sidenote._desktopHandlers = { showSidenote, hideSidenote };
            });
        },
        
        teardown() {
            document.querySelectorAll('.sidenote').forEach(sidenote => {
                const content = sidenote.querySelector('.sidenote-content');
                if (content) content.classList.remove('visible');
                
                if (sidenote._desktopHandlers) {
                    sidenote.removeEventListener('mouseenter', sidenote._desktopHandlers.showSidenote);
                    sidenote.removeEventListener('mouseleave', sidenote._desktopHandlers.hideSidenote);
                    delete sidenote._desktopHandlers;
                }
            });
        },
        
        positionSidenote(sidenote, content) {
            const contentArea = document.getElementById('content');
            if (!contentArea) return;
            
            // Get positions
            const sidenoteRect = sidenote.getBoundingClientRect();
            const contentRect = contentArea.getBoundingClientRect();
            const viewportWidth = window.innerWidth;
            
            // Position sidenote in right margin
            // Start at right edge of content area + small gap
            let leftPos = contentRect.right + 16;
            
            // If not enough room on right, position relative to viewport
            const sidenoteWidth = 240; // var(--sidenote-width)
            if (leftPos + sidenoteWidth > viewportWidth - 16) {
                leftPos = viewportWidth - sidenoteWidth - 16;
            }
            
            // Vertical position: align with the sidenote reference
            let topPos = sidenoteRect.top;
            
            // Keep within viewport bounds
            const maxHeight = 300;
            if (topPos + maxHeight > window.innerHeight - 16) {
                topPos = window.innerHeight - maxHeight - 16;
            }
            if (topPos < 16) topPos = 16;
            
            content.style.left = `${leftPos}px`;
            content.style.top = `${topPos}px`;
        }
    };

    // ============================================
    // MOBILE SIDENOTES
    // Converts sidenotes to expandable inline notes on mobile/tablet
    // ============================================
    
    const MobileSidenotes = {
        init() {
            // Only activate on narrower screens where sidenotes don't fit
            const mql = window.matchMedia('(max-width: 1100px)');
            
            if (mql.matches) {
                this.convertToInline();
            }
            
            // Handle orientation changes / resize
            mql.addEventListener('change', (e) => {
                if (e.matches) {
                    this.convertToInline();
                } else {
                    this.revertToSidenotes();
                }
            });
        },
        
        convertToInline() {
            document.querySelectorAll('.sidenote').forEach((sidenote, index) => {
                // Skip if already converted
                if (sidenote.classList.contains('sidenote-mobile-converted')) return;
                
                const number = sidenote.querySelector('.sidenote-number');
                const content = sidenote.querySelector('.sidenote-content');
                
                if (!content) return;
                
                // Mark as converted
                sidenote.classList.add('sidenote-mobile-converted');
                
                // Create expandable inline note
                const wrapper = document.createElement('span');
                wrapper.className = 'sidenote-mobile-wrapper';
                
                const toggle = document.createElement('button');
                toggle.className = 'sidenote-mobile-toggle';
                toggle.setAttribute('aria-expanded', 'false');
                toggle.setAttribute('aria-label', `Show note ${index + 1}`);
                toggle.innerHTML = `<span class="sidenote-mobile-number">${index + 1}</span>`;
                
                const inlineContent = document.createElement('span');
                inlineContent.className = 'sidenote-mobile-content';
                inlineContent.innerHTML = content.innerHTML;
                inlineContent.hidden = true;
                
                // Toggle behavior
                toggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
                    toggle.setAttribute('aria-expanded', !isExpanded);
                    inlineContent.hidden = isExpanded;
                    toggle.classList.toggle('active', !isExpanded);
                });
                
                wrapper.appendChild(toggle);
                wrapper.appendChild(inlineContent);
                
                // Hide original sidenote elements
                if (number) number.style.display = 'none';
                content.style.display = 'none';
                
                // Insert the mobile version
                sidenote.appendChild(wrapper);
            });
        },
        
        revertToSidenotes() {
            document.querySelectorAll('.sidenote-mobile-converted').forEach(sidenote => {
                const wrapper = sidenote.querySelector('.sidenote-mobile-wrapper');
                const number = sidenote.querySelector('.sidenote-number');
                const content = sidenote.querySelector('.sidenote-content');
                
                if (wrapper) wrapper.remove();
                if (number) number.style.display = '';
                if (content) content.style.display = '';
                
                sidenote.classList.remove('sidenote-mobile-converted');
            });
        }
    };

    // ============================================
    // KEYBOARD SHORTCUTS
    // ============================================
    
    const Keyboard = {
        init() {
            document.addEventListener('keydown', (e) => {
                // Alt+D: Toggle dark mode
                if (e.altKey && (e.key === 'd' || e.key === 'D')) {
                    e.preventDefault();
                    const toggle = document.getElementById('theme-toggle-btn');
                    if (toggle) toggle.click();
                    return;
                }
                
                // Alt+H: Go home
                if (e.altKey && (e.key === 'h' || e.key === 'H')) {
                    e.preventDefault();
                    const isInPages = window.location.pathname.includes('/pages/');
                    const isInWriting = window.location.pathname.includes('/writing/');
                    
                    let homeUrl = 'index.html';
                    if (isInWriting) homeUrl = '../../index.html';
                    else if (isInPages) homeUrl = '../index.html';
                    
                    window.location.href = homeUrl;
                    return;
                }
                
                // / or Ctrl+K: Focus search (if exists)
                if (e.key === '/' || (e.ctrlKey && e.key === 'k')) {
                    const search = document.getElementById('search-input');
                    if (search && document.activeElement !== search) {
                        e.preventDefault();
                        search.focus();
                    }
                }
            });
        }
    };

    // ============================================
    // QUOTE FILTER SYSTEM
    // ============================================
    
    const QuoteFilter = {
        init() {
            const container = document.getElementById('filter-buttons');
            const quotes = document.querySelectorAll('.quote-entry');
            
            if (!container || quotes.length === 0) return;
            
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
            
            const sortedTags = Array.from(allTags).sort();
            
            container.innerHTML = '';
            
            const allBtn = document.createElement('button');
            allBtn.className = 'filter-btn active';
            allBtn.setAttribute('data-filter', 'all');
            allBtn.textContent = 'All';
            container.appendChild(allBtn);
            
            sortedTags.forEach(tag => {
                const btn = document.createElement('button');
                btn.className = 'filter-btn';
                btn.setAttribute('data-filter', tag);
                btn.textContent = tag.charAt(0).toUpperCase() + tag.slice(1);
                container.appendChild(btn);
            });
            
            const filterButtons = container.querySelectorAll('.filter-btn');
            filterButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const filter = button.getAttribute('data-filter');
                    
                    filterButtons.forEach(btn => btn.classList.remove('active'));
                    button.classList.add('active');
                    
                    quotes.forEach(quote => {
                        const tags = quote.getAttribute('data-tags').toLowerCase().split(',').map(t => t.trim());
                        if (filter === 'all' || tags.includes(filter)) {
                            quote.style.display = 'block';
                            quote.classList.add('revealed');
                        } else {
                            quote.style.display = 'none';
                        }
                    });
                });
            });
        }
    };

    // ============================================
    // DEFINITION ALPHABETICAL INDEX
    // ============================================
    
    const DefinitionIndex = {
        init() {
            const container = document.getElementById('alpha-index');
            const definitions = document.querySelectorAll('.definition-entry');
            
            if (!container || definitions.length === 0) return;
            
            const letters = new Set();
            definitions.forEach(def => {
                const letterSpan = def.querySelector('.definition-letter');
                if (letterSpan) {
                    letters.add(letterSpan.textContent.trim().toUpperCase());
                }
            });
            
            const sortedLetters = Array.from(letters).sort();
            
            container.innerHTML = '';
            sortedLetters.forEach(letter => {
                const link = document.createElement('a');
                link.href = '#' + letter;
                link.textContent = letter;
                container.appendChild(link);
                
                definitions.forEach(def => {
                    const letterSpan = def.querySelector('.definition-letter');
                    if (letterSpan && letterSpan.textContent.trim().toUpperCase() === letter) {
                        if (!document.getElementById(letter)) {
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

    // ============================================
    // SMOOTH SCROLLING
    // ============================================
    
    const SmoothScroll = {
        init() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    const href = this.getAttribute('href');
                    if (href !== '#' && href.length > 1) {
                        const target = document.querySelector(href);
                        if (target) {
                            e.preventDefault();
                            target.scrollIntoView({ 
                                behavior: 'smooth', 
                                block: 'start' 
                            });
                            history.pushState(null, null, href);
                        }
                    }
                });
            });
        }
    };

    // ============================================
    // LAZY LOAD IMAGES
    // ============================================
    
    const LazyLoad = {
        init() {
            if (!('IntersectionObserver' in window)) return;
            
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.remove('lazy');
                        }
                        observer.unobserve(img);
                    }
                });
            });
            
            document.querySelectorAll('img.lazy').forEach(img => {
                imageObserver.observe(img);
            });
        }
    };

    // ============================================
    // LION ICON SVG
    // ============================================
    
    const LionIcon = {
        svg: `<svg class="lion-icon" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C8.5 2 5.5 4 4 7c-1 2-1 4 0 6 .5 1 1.2 1.8 2 2.5-.3.8-.5 1.6-.5 2.5 0 2.2 1.8 4 4 4 .8 0 1.6-.3 2.2-.7.2.1.5.2.8.2h1c.3 0 .6-.1.8-.2.6.4 1.4.7 2.2.7 2.2 0 4-1.8 4-4 0-.9-.2-1.7-.5-2.5.8-.7 1.5-1.5 2-2.5 1-2 1-4 0-6-1.5-3-4.5-5-8-5zm-3 8c-.6 0-1-.4-1-1s.4-1 1-1 1 .4 1 1-.4 1-1 1zm6 0c-.6 0-1-.4-1-1s.4-1 1-1 1 .4 1 1-.4 1-1 1zm-3 5c-1.1 0-2-.4-2-1h4c0 .6-.9 1-2 1z"/>
        </svg>`,
        
        init() {
            const navTitle = document.querySelector('.nav-header h1 a');
            if (navTitle && !navTitle.querySelector('.lion-icon')) {
                navTitle.insertAdjacentHTML('beforeend', this.svg);
            }
        }
    };

    // ============================================
    // CONSOLE EASTER EGG
    // ============================================
    
    const ConsoleEasterEgg = {
        init() {
            const styles = {
                title: 'font-size: 24px; font-weight: bold; font-style: italic; color: #B8860B;',
                quote: 'font-size: 14px; color: #666; font-style: italic;',
                info: 'font-size: 11px; color: #888;'
            };
            
            console.log('%cH. Aslan', styles.title);
            console.log('%c"Not a tame lion."', styles.quote);
            console.log('%c— C.S. Lewis, The Chronicles of Narnia', styles.info);
            console.log('%c\nKeyboard shortcuts:', styles.info);
            console.log('%c  Alt+D → Toggle dark mode', styles.info);
            console.log('%c  Alt+H → Return home', styles.info);
            console.log('%c\n"He is not safe, but he is good."', styles.quote);
        }
    };

    // ============================================
    // UTILITIES
    // ============================================
    
    const Utils = {
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
        
        formatDate(date) {
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            return new Date(date).toLocaleDateString('en-US', options);
        },
        
        getReadingTime(text) {
            const wordsPerMinute = 200;
            const words = text.trim().split(/\s+/).length;
            const minutes = Math.ceil(words / wordsPerMinute);
            return `${minutes} min read`;
        }
    };

    // ============================================
    // INITIALIZATION
    // ============================================
    
    function init() {
        // Initialize loading screen first (handles its own visibility)
        LoadingScreen.init();
        
        // Core functionality
        DarkMode.init();
        ReadingProgress.init();
        ScrollReveal.init();
        AutoEnhance.init();
        LinkPopup.init();
        DesktopSidenotes.init();
        MobileSidenotes.init();
        Keyboard.init();
        SmoothScroll.init();
        LazyLoad.init();
        LionIcon.init();
        
        // Page-specific
        QuoteFilter.init();
        DefinitionIndex.init();
        
        // Easter egg
        ConsoleEasterEgg.init();
    }
    
    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Export for potential external use
    window.WikiEnhance = {
        Utils,
        DarkMode,
        LinkPopup,
        AutoEnhance,
        LoadingScreen,
        DesktopSidenotes,
        MobileSidenotes
    };

})();
