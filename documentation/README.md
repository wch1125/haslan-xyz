# H. Aslan Wiki

A personal wiki inspired by Gwern.net, featuring advanced typography, sidenotes, collapsible sections, link previews, and automated content management.

## Features

- **Gwern-inspired Design**: Clean, readable monochrome aesthetic with advanced typography
- **Dark Mode**: Toggle between light and dark themes (Alt+D)
- **Sidenotes**: Tufte-style marginal notes (desktop only)
- **Dropcaps**: Elegant first-letter styling
- **Link Previews**: Hover over internal links to see page excerpts
- **Definition System**: Hover over capitalized Defined Terms to see definitions
- **Collapsible Sections**: Progressive disclosure with state persistence
- **Keyboard Shortcuts**: Alt+D (dark mode), Alt+H (home)
- **Mobile Responsive**: Adapts gracefully to all screen sizes
- **Automated Content**: Python scripts to add quotes, definitions, and writing pieces

## Project Structure

```
has-lan-wiki/
├── index.html              # Homepage
├── assets/
│   ├── css/
│   │   └── style.css       # Main stylesheet
│   └── js/
│       └── script.js       # JavaScript functionality
├── pages/
│   ├── quotes.html         # Quotes collection with filtering
│   ├── definitions.html    # Glossary of Defined Terms
│   ├── creative-writing.html  # Writing index
│   ├── contact.html        # Contact page
│   └── writing/            # Individual writing pieces
├── scripts/
│   ├── add-quote.py        # Add new quotes
│   ├── add-definition.py   # Add new definitions
│   └── add-writing.py      # Add new writing pieces
├── templates/              # HTML templates
├── robots.txt              # Search engine directives
├── CNAME                   # Custom domain (if using GitHub Pages)
└── README.md               # This file
```

## Setup

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/has-lan-wiki.git
cd has-lan-wiki
```

2. Open `index.html` in your browser:
```bash
open index.html  # macOS
xdg-open index.html  # Linux
start index.html  # Windows
```

Or use a local server:
```bash
python -m http.server 8000
# Then visit http://localhost:8000
```

### GitHub Pages Deployment

1. Push your repository to GitHub
2. Go to Settings → Pages
3. Select branch: `main` (or `master`)
4. Select folder: `/ (root)`
5. Save

Your site will be available at `https://yourusername.github.io/has-lan-wiki/`

### Custom Domain

1. Create a `CNAME` file in the root directory with your domain:
```
yourdomain.com
```

2. Configure DNS records with your domain provider:
   - Add a CNAME record pointing to `yourusername.github.io`
   - Or add A records pointing to GitHub's IPs (see [GitHub docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site))

## Adding Content

### Adding Quotes

```bash
python scripts/add-quote.py
```

The script will prompt you for:
- Quote text (can be multiple lines)
- Author
- Source (book, article, etc.)
- Year (optional)
- Tags (comma-separated)

The quote will be automatically added to `pages/quotes.html` with proper formatting.

**Manual Method**: Copy this template into `pages/quotes.html`:

```html
<div class="quote-entry" data-tags="tag1,tag2,tag3" data-date="YYYY-MM-DD">
    <blockquote class="quote-text">
        Quote text here
    </blockquote>
    <div class="quote-attribution">
        <span class="quote-author">Author Name</span>
        <span class="quote-source">Source (Year)</span>
    </div>
    <div class="quote-metadata">
        <div class="quote-tags">
            <span class="quote-tag">tag1</span>
            <span class="quote-tag">tag2</span>
        </div>
        <time class="quote-date" datetime="YYYY-MM-DD">Added Month Year</time>
    </div>
</div>
```

### Adding Definitions

```bash
python scripts/add-definition.py
```

The script will prompt you for:
- Term name
- Definition paragraphs
- Related terms (optional)

The definition will be automatically added to `pages/definitions.html`.

**Using Definitions in Other Pages**:

```html
<a href="pages/definitions.html#term-slug" 
   class="definition-link" 
   data-term="Term Name" 
   data-definition="Brief definition for hover preview">Term Name</a>
```

Example:
```html
Her work showed remarkable 
<a href="pages/definitions.html#authenticity" 
   class="definition-link" 
   data-term="Authenticity" 
   data-definition="The quality of acting from genuine internal motivation rather than external expectation.">Authenticity</a>.
```

### Adding Creative Writing

```bash
python scripts/add-writing.py
```

The script will prompt you for:
- Title
- Category (Short Story, Poem, Essay, Fragment, etc.)
- Brief excerpt
- Content (type 'END' on a new line when finished)

The script will:
1. Create a new page in `pages/writing/`
2. Add an entry to the creative writing index
3. Set up proper navigation and metadata

## Customization

### Changing the Site Name

Replace `H. Aslan` with your desired name in:
- `index.html` (nav header)
- All page files in `pages/` (nav headers)
- `assets/js/script.js` (console message)
- `README.md`

### Modifying Colors

Edit CSS variables in `assets/css/style.css`:

```css
:root {
    --bg-primary: #fff;
    --text-primary: #000;
    --link-color: #00e;
    /* etc. */
}

[data-theme="dark"] {
    --bg-primary: #111;
    --text-primary: #ddd;
    /* etc. */
}
```

### Adding New Navigation Links

Edit the `<nav id="sidenav">` section in each HTML file:

```html
<section class="nav-section">
    <h2>Section Name</h2>
    <ul>
        <li><a href="page.html">Page Name</a></li>
    </ul>
</section>
```

### Adding New Page Types

1. Copy an existing page as a template
2. Modify the content structure as needed
3. Add to navigation in all pages
4. (Optional) Create a script in `scripts/` to automate additions

## Advanced Features

### Sidenotes

```html
<p>Main text with a sidenote<span class="sidenote">
    <span class="sidenote-number"></span>
    <span class="sidenote-content">This is the sidenote text.</span>
</span> continuing after.</p>
```

Sidenotes automatically number themselves and appear in the margin on desktop. On mobile, they convert to inline footnotes.

### Dropcaps

```html
<p><span class="dropcap">T</span>his paragraph starts with a dropcap.</p>
```

### Collapsible Sections

```html
<details class="collapse">
    <summary>Click to expand</summary>
    <div class="collapse-content">
        <p>Hidden content here.</p>
    </div>
</details>
```

State is preserved in localStorage between visits.

### Smallcaps

```html
<span class="smallcaps">NYC</span> or <span class="smallcaps">usa</span>
```

### Link Popups

Add excerpts to `assets/js/script.js` in the `LinkPopup.excerpts` object:

```javascript
excerpts: {
    'pages/your-page.html': {
        title: 'Page Title',
        text: 'Brief description that appears in popup preview.'
    }
}
```

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Grid and Flexbox
- CSS Custom Properties
- LocalStorage for theme and collapse state
- Intersection Observer for lazy loading (progressive enhancement)

## Performance

- Minimal JavaScript (~10KB)
- CSS-only animations and transitions
- Lazy loading for images
- No external dependencies (except CDN for optional features)
- Static HTML for fast loading

## Privacy

- No analytics by default
- No cookies (only localStorage for preferences)
- No external tracking
- `robots.txt` blocks AI scrapers

To add privacy-respecting analytics:
- [Plausible](https://plausible.io/)
- [Simple Analytics](https://simpleanalytics.com/)
- [Ackee](https://github.com/electerious/Ackee) (self-hosted)

## Keyboard Shortcuts

- `Alt+D` - Toggle dark mode
- `Alt+H` - Go to homepage

Additional shortcuts can be added in `assets/js/script.js`.

## Maintenance

### Making Scripts Executable

```bash
chmod +x scripts/*.py
```

### Updating Last Modified Dates

Update the `<time>` elements in page headers when making significant changes:

```html
<time datetime="2025-12-08">8 December 2025</time>
```

### Backing Up Content

Your content is stored in:
- `pages/quotes.html` - All quotes
- `pages/definitions.html` - All definitions  
- `pages/writing/*.html` - Individual writing pieces

Regular git commits provide version history and backups.

## Troubleshooting

### Link Previews Not Working

- Check that you're on a desktop device (hover capability required)
- Verify the page path exists in `LinkPopup.excerpts` in `script.js`
- Check browser console for JavaScript errors

### Scripts Not Running

- Ensure Python 3 is installed: `python3 --version`
- Make scripts executable: `chmod +x scripts/*.py`
- Check file paths match your directory structure

### Dark Mode Not Persisting

- Ensure JavaScript is enabled
- Check that localStorage is not disabled in browser settings
- Try clearing localStorage: `localStorage.clear()` in console

### GitHub Pages Not Updating

- Check the Actions tab for build status
- Ensure you've pushed to the correct branch
- Clear browser cache
- GitHub Pages can take a few minutes to update

## Credits

Design and functionality inspired by:
- [Gwern.net](https://gwern.net) - Overall aesthetic and features
- [Edward Tufte](https://www.edwardtufte.com/) - Sidenote design
- [Butterick's Practical Typography](https://practicaltypography.com/) - Typography principles

## License

MIT License - feel free to use this as a template for your own wiki.

## Contact

Update `pages/contact.html` with your preferred contact method.

---

**Last updated**: December 2025
