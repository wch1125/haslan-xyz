# H. Aslan Wiki

*"Not a tame lion."*

A personal wiki inspired by [Gwern.net](https://gwern.net), featuring premium animations, Tufte-style sidenotes, and subtle references to Aslan from C.S. Lewis's Chronicles of Narnia.

## Recent Updates (December 2025)

Based on feedback, several improvements have been made:

### UX Improvements
- **Conditional loading screen** — Only shows on first visit per session; respects `prefers-reduced-motion`; skippable
- **Skip-to-content link** — Accessibility improvement for keyboard navigation
- **Hospitality-first homepage** — Clearer entry points with "Start Here" section
- **Content badges** — Essays, Sketches, Notebooks, Fiction, and Draft labels help readers know what they're getting into
- **"Now" section** — What I'm currently thinking about, making, and reading
- **Colophon page** — How the site is built, for those who want to make their own

### Navigation Restructure
- Simplified to "Explore" (content) and "Meta" (about/contact)
- Removed Demo from main nav (still accessible)
- Added Colophon link

### Content Organization
- Writing page now has Published and Workbench sections
- Drafts are explicitly labeled, not hidden
- "Good faith objections" collapsibles on essays

## Features

### Core Features
- **Defined Terms System** — Capitalized terms auto-link to definitions with hover previews
- **Sidenotes** — Tufte-style marginal notes (desktop) or inline notes (mobile)
- **Collapsible Sections** — Progressive disclosure for detailed content
- **Quote Collection** — Filterable quotes by tags
- **Creative Writing** — Index linking to individual pieces

### Premium Interactions
- **Loading Screen** — Golden motes animation (conditional, skippable)
- **Reading Progress Bar** — Shows scroll position through articles
- **Scroll Reveal** — Elements animate in as you scroll
- **Enhanced Popups** — Smooth definition previews with golden accents
- **Dark Mode** — Smooth theme transitions with saved preference

### Lion Motif (Subtle)
- **Accent Color** — Lion's mane gold (`#B8860B`)
- **Hidden Icon** — Lion silhouette appears when hovering "H. Aslan" in nav
- **Paw Dividers** — Subtle paw prints between some sections
- **Console Easter Eggs** — Open dev tools for Narnia quotes
- **Favicon** — Minimalist lion face

## File Structure

```
/
├── index.html                 # Homepage (hospitality-first design)
├── wiki-manager.py            # Flask tool for adding content
├── README.md                  # This file
├── assets/
│   ├── css/
│   │   └── style.css          # All styles including animations
│   └── js/
│       └── script.js          # All JavaScript functionality
└── pages/
    ├── definitions.html       # Glossary of Defined Terms
    ├── quotes.html            # Quote collection
    ├── creative-writing.html  # Writing index (Published + Workbench)
    ├── personal-domain.html   # Essay on narrative sovereignty
    ├── colophon.html          # How this site is built
    ├── contact.html           # Contact + "show me your site"
    ├── demo.html              # Feature demonstration
    └── writing/
        └── [pieces].html      # Individual writing pieces
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Alt + D` | Toggle dark mode |
| `Alt + H` | Go to homepage |

## Content Badges

Essays and creative pieces now have status badges:

- **Essay** — Argued and structured
- **Sketch** — Speculative, exploring
- **Notebook** — Working notes, rough
- **Fiction** — Creative work
- **Draft** — Unfinished, visible for accountability

## Wiki Manager

Add content via the Flask-based wiki manager:

```bash
pip install flask
python wiki-manager.py
open http://localhost:5000
```

After adding content:
```bash
git add . && git commit -m "Add new content" && git push
```

## Accessibility

- Skip-to-content link on all pages
- `aria-label` on navigation
- Respects `prefers-reduced-motion`
- Works without JavaScript
- Keyboard shortcuts documented

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Graceful degradation for older browsers
- Works without JavaScript (core content accessible)

## Credits

- Design inspired by [Gwern.net](https://gwern.net)
- Sidenotes inspired by [Edward Tufte](https://edwardtufte.github.io/tufte-css/)
- Lion motif references C.S. Lewis's *The Chronicles of Narnia*

---

*"He is not safe, but he is good."* — Mr. Beaver, The Lion, the Witch and the Wardrobe
