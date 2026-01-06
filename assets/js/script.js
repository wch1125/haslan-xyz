/* ============================================
   H. ASLAN WIKI - ENHANCED JAVASCRIPT
   "Not a tame lion."
   ============================================ */

(function() {
    'use strict';

    /* ============================================
       MOBILE NAV MODULE
       Collapsible hamburger menu for mobile
       ============================================ */
    const MobileNav = {
        sidenav: null,
        toggleBtn: null,
        isOpen: false,

        init() {
            this.sidenav = document.getElementById('sidenav');
            if (!this.sidenav) return;

            this.createToggleButton();
            this.bindEvents();
            this.checkInitialState();
        },

        createToggleButton() {
            this.toggleBtn = document.createElement('button');
            this.toggleBtn.className = 'mobile-nav-toggle';
            this.toggleBtn.setAttribute('aria-label', 'Toggle navigation menu');
            this.toggleBtn.setAttribute('aria-expanded', 'false');
            this.toggleBtn.innerHTML = `
                <span class="hamburger">☰</span>
                <span class="close">✕</span>
            `;
            document.body.appendChild(this.toggleBtn);
        },

        bindEvents() {
            this.toggleBtn.addEventListener('click', () => this.toggle());
            
            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });

            // Close when clicking a nav link (on mobile)
            this.sidenav.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    if (window.innerWidth <= 900) {
                        this.close();
                    }
                });
            });

            // Close when clicking outside (on overlay)
            document.addEventListener('click', (e) => {
                if (this.isOpen && 
                    !this.sidenav.contains(e.target) && 
                    !this.toggleBtn.contains(e.target)) {
                    this.close();
                }
            });
        },

        checkInitialState() {
            // Start closed on mobile
            if (window.innerWidth <= 900) {
                this.sidenav.classList.add('collapsed');
            }
        },

        toggle() {
            this.isOpen ? this.close() : this.open();
        },

        open() {
            this.isOpen = true;
            this.sidenav.classList.remove('collapsed');
            this.sidenav.classList.add('mobile-open');
            this.toggleBtn.classList.add('open');
            this.toggleBtn.setAttribute('aria-expanded', 'true');
            document.body.classList.add('nav-open');
        },

        close() {
            this.isOpen = false;
            this.sidenav.classList.add('collapsed');
            this.sidenav.classList.remove('mobile-open');
            this.toggleBtn.classList.remove('open');
            this.toggleBtn.setAttribute('aria-expanded', 'false');
            document.body.classList.remove('nav-open');
        }
    };

    /* ============================================
       LOADING SCREEN MODULE
       Shows lion animation once per session
       ============================================ */
    const LoadingScreen = {
        init() {
            const loader = document.querySelector('.loading-screen');
            if (!loader) return;

            // Skip if already shown this session or user prefers reduced motion
            const hasShown = sessionStorage.getItem('loadingShown');
            const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

            if (hasShown || prefersReduced) {
                loader.remove();
                return;
            }

            // Show loading screen
            loader.classList.add('active');
            
            // Hide after animation completes
            setTimeout(() => {
                loader.classList.add('fade-out');
                setTimeout(() => {
                    loader.remove();
                    sessionStorage.setItem('loadingShown', 'true');
                }, 500);
            }, 1800);
        }
    };

    /* ============================================
       READING PROGRESS MODULE
       Progress bar at top of page
       ============================================ */
    const ReadingProgress = {
        bar: null,
        throttleTimer: null,

        init() {
            this.createBar();
            this.bindEvents();
        },

        createBar() {
            this.bar = document.createElement('div');
            this.bar.className = 'reading-progress';
            this.bar.setAttribute('role', 'progressbar');
            this.bar.setAttribute('aria-label', 'Reading progress');
            document.body.appendChild(this.bar);
        },

        bindEvents() {
            window.addEventListener('scroll', () => this.throttledUpdate(), { passive: true });
            window.addEventListener('resize', () => this.throttledUpdate(), { passive: true });
        },

        throttledUpdate() {
            if (this.throttleTimer) return;
            this.throttleTimer = setTimeout(() => {
                this.update();
                this.throttleTimer = null;
            }, 16); // ~60fps
        },

        update() {
            const scrollTop = window.scrollY;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
            
            this.bar.style.width = `${Math.min(progress, 100)}%`;
            this.bar.setAttribute('aria-valuenow', Math.round(progress));
        }
    };

    /* ============================================
       SCROLL REVEAL MODULE
       Progressive content reveal on scroll
       ============================================ */
    const ScrollReveal = {
        init() {
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

            const observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('revealed');
                            observer.unobserve(entry.target);
                        }
                    });
                },
                { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
            );

            // Target elements for reveal animation
            const selectors = [
                '.entry-content p',
                '.entry-content h2',
                '.entry-content h3',
                '.entry-content blockquote',
                '.topic-section',
                '.writing-entry'
            ];

            document.querySelectorAll(selectors.join(', ')).forEach((el, index) => {
                el.style.transitionDelay = `${Math.min(index * 50, 300)}ms`;
                el.classList.add('reveal-target');
                observer.observe(el);
            });
        }
    };

    /* ============================================
       AUTO ENHANCE MODULE
       Dropcaps, term linking, verse detection
       ============================================ */
    const AutoEnhance = {
        definitions: {},

        async init() {
            await this.loadDefinitions();
            this.applyDropcaps();
            this.autoLinkTerms();
            this.detectVerseFormatting();
        },

        async loadDefinitions() {
            try {
                const response = await fetch('/definitions.html');
                if (!response.ok) return;
                
                const html = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                // Extract terms from definition list
                doc.querySelectorAll('dt').forEach(dt => {
                    const term = dt.textContent.trim().toLowerCase();
                    const dd = dt.nextElementSibling;
                    if (dd && dd.tagName === 'DD') {
                        this.definitions[term] = {
                            term: dt.textContent.trim(),
                            definition: dd.innerHTML
                        };
                    }
                });
            } catch (e) {
                console.log('Definitions not loaded:', e);
            }
        },

        applyDropcaps() {
            const firstParagraph = document.querySelector('.entry-content > p:first-of-type');
            if (!firstParagraph) return;

            const text = firstParagraph.innerHTML;
            const firstChar = text.charAt(0);
            
            // Only apply to letters
            if (/[A-Z]/.test(firstChar)) {
                firstParagraph.innerHTML = 
                    `<span class="dropcap">${firstChar}</span>${text.substring(1)}`;
            }
        },

        autoLinkTerms() {
            if (Object.keys(this.definitions).length === 0) return;

            const content = document.querySelector('.entry-content');
            if (!content) return;

            // Walk through text nodes only
            const walker = document.createTreeWalker(
                content,
                NodeFilter.SHOW_TEXT,
                {
                    acceptNode: (node) => {
                        // Skip if inside a link, heading, or code
                        const parent = node.parentElement;
                        if (!parent) return NodeFilter.FILTER_REJECT;
                        const tagName = parent.tagName.toLowerCase();
                        if (['a', 'h1', 'h2', 'h3', 'code', 'pre', 'script'].includes(tagName)) {
                            return NodeFilter.FILTER_REJECT;
                        }
                        return NodeFilter.FILTER_ACCEPT;
                    }
                }
            );

            const nodesToReplace = [];
            let node;
            while (node = walker.nextNode()) {
                for (const [termLower, termData] of Object.entries(this.definitions)) {
                    const regex = new RegExp(`\\b(${termData.term})\\b`, 'gi');
                    if (regex.test(node.textContent)) {
                        nodesToReplace.push({ node, termLower, termData, regex });
                        break; // One term per text node to avoid conflicts
                    }
                }
            }

            // Replace nodes with linked versions
            nodesToReplace.forEach(({ node, termData, regex }) => {
                const span = document.createElement('span');
                span.innerHTML = node.textContent.replace(
                    regex,
                    `<a href="/definitions.html#${termData.term.toLowerCase().replace(/\s+/g, '-')}" class="term-link" data-term="${termData.term}">$1</a>`
                );
                node.parentNode.replaceChild(span, node);
            });
        },

        detectVerseFormatting() {
            const content = document.querySelector('.entry-content');
            if (!content) return;

            // Find paragraphs that look like verse (short lines with line breaks)
            content.querySelectorAll('p').forEach(p => {
                const text = p.innerHTML;
                const lines = text.split('<br>').filter(l => l.trim());
                
                // Heuristic: if multiple short lines, treat as verse
                if (lines.length >= 3 && lines.every(l => l.trim().length < 60)) {
                    p.classList.add('verse');
                }
            });
        }
    };

    /* ============================================
       DARK MODE MODULE
       Toggle with localStorage persistence
       ============================================ */
    const DarkMode = {
        toggle: null,
        
        init() {
            this.createToggle();
            this.loadPreference();
            this.bindEvents();
        },

        createToggle() {
            this.toggle = document.createElement('button');
            this.toggle.className = 'dark-mode-toggle';
            this.toggle.setAttribute('aria-label', 'Toggle dark mode');
            this.toggle.innerHTML = `
                <span class="sun">☀️</span>
                <span class="moon">🌙</span>
            `;
            
            // Add to sidenav if exists, otherwise to body
            const sidenav = document.getElementById('sidenav');
            if (sidenav) {
                const footer = sidenav.querySelector('.sidenav-footer') || sidenav;
                footer.appendChild(this.toggle);
            } else {
                document.body.appendChild(this.toggle);
            }
        },

        loadPreference() {
            const saved = localStorage.getItem('theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            if (saved === 'dark' || (!saved && prefersDark)) {
                document.documentElement.setAttribute('data-theme', 'dark');
                this.updateToggle(true);
            }
        },

        bindEvents() {
            this.toggle.addEventListener('click', () => this.toggleTheme());
            
            // Listen for system preference changes
            window.matchMedia('(prefers-color-scheme: dark)')
                .addEventListener('change', (e) => {
                    if (!localStorage.getItem('theme')) {
                        this.setTheme(e.matches);
                    }
                });
        },

        toggleTheme() {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            this.setTheme(!isDark);
        },

        setTheme(dark) {
            document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
            localStorage.setItem('theme', dark ? 'dark' : 'light');
            this.updateToggle(dark);
        },

        updateToggle(isDark) {
            this.toggle.classList.toggle('dark', isDark);
        }
    };

    /* ============================================
       LINK POPUP MODULE
       Definition previews on hover/tap
       ============================================ */
    const LinkPopup = {
        popup: null,
        isTouchDevice: false,
        hideTimeout: null,

        init() {
            this.isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
            this.createPopup();
            this.bindEvents();
        },

        createPopup() {
            this.popup = document.createElement('div');
            this.popup.className = 'link-popup';
            this.popup.setAttribute('role', 'tooltip');
            this.popup.hidden = true;
            document.body.appendChild(this.popup);
        },

        bindEvents() {
            document.addEventListener('mouseover', (e) => {
                if (this.isTouchDevice) return;
                const link = e.target.closest('.term-link, a[data-preview]');
                if (link) this.showForLink(link);
            });

            document.addEventListener('mouseout', (e) => {
                if (this.isTouchDevice) return;
                const link = e.target.closest('.term-link, a[data-preview]');
                if (link) this.scheduleHide();
            });

            // Touch handling
            document.addEventListener('touchstart', (e) => {
                const link = e.target.closest('.term-link, a[data-preview]');
                if (link) {
                    e.preventDefault();
                    this.toggleForLink(link);
                } else if (!this.popup.contains(e.target)) {
                    this.hide();
                }
            });

            // Keep popup visible while hovering it
            this.popup.addEventListener('mouseenter', () => {
                clearTimeout(this.hideTimeout);
            });

            this.popup.addEventListener('mouseleave', () => {
                this.scheduleHide();
            });
        },

        async showForLink(link) {
            clearTimeout(this.hideTimeout);
            
            const term = link.dataset.term;
            let content = '';

            if (term && AutoEnhance.definitions[term.toLowerCase()]) {
                const def = AutoEnhance.definitions[term.toLowerCase()];
                content = `<strong>${def.term}</strong><p>${def.definition}</p>`;
            } else if (link.dataset.preview) {
                content = link.dataset.preview;
            } else {
                return; // No preview available
            }

            this.popup.innerHTML = content;
            this.popup.hidden = false;
            this.positionNear(link);
        },

        toggleForLink(link) {
            if (!this.popup.hidden && this.popup.dataset.currentLink === link.href) {
                this.hide();
            } else {
                this.popup.dataset.currentLink = link.href;
                this.showForLink(link);
            }
        },

        positionNear(element) {
            const rect = element.getBoundingClientRect();
            const popupRect = this.popup.getBoundingClientRect();
            
            let top = rect.bottom + 8;
            let left = rect.left;

            // Adjust if would go off screen
            if (left + popupRect.width > window.innerWidth - 16) {
                left = window.innerWidth - popupRect.width - 16;
            }
            if (top + popupRect.height > window.innerHeight - 16) {
                top = rect.top - popupRect.height - 8;
            }

            this.popup.style.top = `${top + window.scrollY}px`;
            this.popup.style.left = `${Math.max(16, left)}px`;
        },

        scheduleHide() {
            this.hideTimeout = setTimeout(() => this.hide(), 200);
        },

        hide() {
            this.popup.hidden = true;
            delete this.popup.dataset.currentLink;
        }
    };

    /* ============================================
       DESKTOP SIDENOTES MODULE
       Gwern-style marginal notes
       ============================================ */
    const DesktopSidenotes = {
        init() {
            if (window.innerWidth < 1100) return;

            this.positionSidenotes();
            window.addEventListener('resize', () => this.handleResize());
        },

        positionSidenotes() {
            const sidenotes = document.querySelectorAll('.sidenote');
            const content = document.querySelector('.entry-content');
            if (!content || sidenotes.length === 0) return;

            const contentRect = content.getBoundingClientRect();
            let lastBottom = 0;

            sidenotes.forEach((note, index) => {
                const ref = document.querySelector(`[data-sidenote="${index + 1}"]`);
                if (!ref) return;

                const refRect = ref.getBoundingClientRect();
                let idealTop = refRect.top - contentRect.top;
                
                // Prevent overlap with previous sidenote
                if (idealTop < lastBottom + 16) {
                    idealTop = lastBottom + 16;
                }

                note.style.position = 'absolute';
                note.style.top = `${idealTop}px`;
                note.style.right = `-${260}px`;
                note.style.width = '240px';

                lastBottom = idealTop + note.offsetHeight;
            });
        },

        handleResize() {
            if (window.innerWidth >= 1100) {
                this.positionSidenotes();
            } else {
                // Reset positioning for mobile
                document.querySelectorAll('.sidenote').forEach(note => {
                    note.style.position = '';
                    note.style.top = '';
                    note.style.right = '';
                    note.style.width = '';
                });
            }
        }
    };

    /* ============================================
       COLLAPSIBLE SECTIONS MODULE
       Expandable content blocks
       ============================================ */
    const Collapsibles = {
        init() {
            document.querySelectorAll('.collapsible-header').forEach(header => {
                header.addEventListener('click', () => this.toggle(header));
                header.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        this.toggle(header);
                    }
                });
            });
        },

        toggle(header) {
            const content = header.nextElementSibling;
            if (!content || !content.classList.contains('collapsible-content')) return;

            const isExpanded = header.getAttribute('aria-expanded') === 'true';
            
            header.setAttribute('aria-expanded', !isExpanded);
            content.hidden = isExpanded;
            
            if (!isExpanded) {
                content.style.maxHeight = content.scrollHeight + 'px';
            } else {
                content.style.maxHeight = '0';
            }
        }
    };

    /* ============================================
       TABLE OF CONTENTS MODULE
       Auto-generate from headings
       ============================================ */
    const TableOfContents = {
        init() {
            const tocContainer = document.querySelector('.toc');
            if (!tocContainer) return;
            
            // Skip if TOC already has content (manually created)
            if (tocContainer.querySelector('ul')) return;

            const headings = document.querySelectorAll('.entry-content h2, .entry-content h3');
            if (headings.length < 3) {
                tocContainer.hidden = true;
                return;
            }

            const list = document.createElement('ul');
            
            headings.forEach((heading, index) => {
                // Ensure heading has an ID
                if (!heading.id) {
                    heading.id = `section-${index + 1}`;
                }

                const li = document.createElement('li');
                li.className = heading.tagName.toLowerCase();
                
                const link = document.createElement('a');
                link.href = `#${heading.id}`;
                link.textContent = heading.textContent;
                
                li.appendChild(link);
                list.appendChild(li);
            });

            tocContainer.appendChild(list);
        }
    };

    /* ============================================
       SMOOTH SCROLL MODULE
       Animated anchor navigation
       ============================================ */
    const SmoothScroll = {
        init() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', (e) => {
                    const targetId = anchor.getAttribute('href');
                    if (targetId === '#') return;

                    const target = document.querySelector(targetId);
                    if (target) {
                        e.preventDefault();
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                        
                        // Update URL without jumping
                        history.pushState(null, '', targetId);
                    }
                });
            });
        }
    };

    /* ============================================
       EXTERNAL LINK HANDLER
       Mark and handle external links
       ============================================ */
    const ExternalLinks = {
        init() {
            const currentHost = window.location.hostname;
            
            document.querySelectorAll('a[href^="http"]').forEach(link => {
                try {
                    const url = new URL(link.href);
                    if (url.hostname !== currentHost) {
                        link.classList.add('external');
                        link.setAttribute('target', '_blank');
                        link.setAttribute('rel', 'noopener noreferrer');
                        
                        // Add visual indicator if not already present
                        if (!link.querySelector('.external-icon')) {
                            const icon = document.createElement('span');
                            icon.className = 'external-icon';
                            icon.setAttribute('aria-hidden', 'true');
                            icon.textContent = '↗';
                            link.appendChild(icon);
                        }
                    }
                } catch (e) {
                    // Invalid URL, skip
                }
            });
        }
    };

    /* ============================================
       KEYBOARD NAVIGATION
       Vim-style shortcuts
       ============================================ */
    const KeyboardNav = {
        init() {
            document.addEventListener('keydown', (e) => {
                // Skip if typing in input/textarea
                if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;
                if (e.ctrlKey || e.metaKey || e.altKey) return;

                switch(e.key.toLowerCase()) {
                    case 'g':
                        // Go to top
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                        break;
                    case 'shift':
                        // G = Go to bottom (need to check for Shift+G)
                        break;
                    case 'j':
                        // Scroll down
                        window.scrollBy({ top: 100, behavior: 'smooth' });
                        break;
                    case 'k':
                        // Scroll up
                        window.scrollBy({ top: -100, behavior: 'smooth' });
                        break;
                    case '/':
                        // Focus search if exists
                        const search = document.querySelector('input[type="search"], .search-input');
                        if (search) {
                            e.preventDefault();
                            search.focus();
                        }
                        break;
                }
            });

            // Handle Shift+G for go to bottom
            let shiftPressed = false;
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Shift') shiftPressed = true;
                if (e.key.toLowerCase() === 'g' && shiftPressed) {
                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                }
            });
            document.addEventListener('keyup', (e) => {
                if (e.key === 'Shift') shiftPressed = false;
            });
        }
    };

    /* ============================================
       COPY CODE BLOCKS
       Add copy button to code blocks
       ============================================ */
    const CopyCode = {
        init() {
            document.querySelectorAll('pre code').forEach(block => {
                const wrapper = document.createElement('div');
                wrapper.className = 'code-block-wrapper';
                
                const button = document.createElement('button');
                button.className = 'copy-code-btn';
                button.textContent = 'Copy';
                button.setAttribute('aria-label', 'Copy code to clipboard');
                
                button.addEventListener('click', async () => {
                    try {
                        await navigator.clipboard.writeText(block.textContent);
                        button.textContent = 'Copied!';
                        button.classList.add('copied');
                        setTimeout(() => {
                            button.textContent = 'Copy';
                            button.classList.remove('copied');
                        }, 2000);
                    } catch (e) {
                        button.textContent = 'Failed';
                        setTimeout(() => {
                            button.textContent = 'Copy';
                        }, 2000);
                    }
                });

                block.parentNode.insertBefore(wrapper, block);
                wrapper.appendChild(block);
                wrapper.appendChild(button);
            });
        }
    };

    /* ============================================
       INITIALIZE ALL MODULES
       ============================================ */
    function init() {
        // Core functionality
        MobileNav.init();
        LoadingScreen.init();
        ReadingProgress.init();
        DarkMode.init();
        
        // Content enhancement
        AutoEnhance.init();
        ScrollReveal.init();
        DesktopSidenotes.init();
        Collapsibles.init();
        TableOfContents.init();
        
        // Navigation & UX
        SmoothScroll.init();
        ExternalLinks.init();
        LinkPopup.init();
        KeyboardNav.init();
        CopyCode.init();
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
