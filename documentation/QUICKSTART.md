# H. Aslan Wiki - Quick Start Guide

## Immediate Steps After Downloading

### 1. Customize Your Identity

Replace "H. Aslan" with your pseudonym in these files:
- `index.html` - Line 7 (title), Line 47 (nav header)
- All files in `pages/` - Update nav headers
- `assets/js/script.js` - Line 362 (console message)

**Quick find & replace:**
```bash
# macOS/Linux
grep -rl "H. Aslan" . | xargs sed -i '' 's/H. Aslan/YourName/g'

# Linux (without the '')
grep -rl "H. Aslan" . | xargs sed -i 's/H. Aslan/YourName/g'
```

### 2. Update Contact Information

Edit `pages/contact.html`:
- Replace `your.email@example.com` with your actual email
- Add your social media links
- Customize the contact sections

### 3. Test Locally

```bash
# Navigate to the directory
cd has-lan-wiki

# Start a local server
python3 -m http.server 8000

# Open in browser
# Visit: http://localhost:8000
```

### 4. Add Your First Content

**Add a quote:**
```bash
python3 scripts/add-quote.py
```

**Add a definition:**
```bash
python3 scripts/add-definition.py
```

**Add a writing piece:**
```bash
python3 scripts/add-writing.py
```

### 5. Deploy to GitHub Pages

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - H. Aslan Wiki"

# Create repository on GitHub, then:
git remote add origin https://github.com/yourusername/your-repo-name.git
git branch -M main
git push -u origin main

# Enable GitHub Pages
# Go to: Settings → Pages → Source: main branch → / (root) → Save
```

Your site will be live at: `https://yourusername.github.io/your-repo-name/`

## Daily Workflow

### Adding Content Without Scripts

**For quick additions, you can edit HTML directly:**

1. Open the relevant file (`pages/quotes.html`, `pages/definitions.html`, etc.)
2. Find the appropriate section
3. Copy an existing entry as a template
4. Modify the content
5. Save and commit

### Using the Automation Scripts

**Best practice for regular updates:**

```bash
# Add new quote
./scripts/add-quote.py

# Add new definition
./scripts/add-definition.py

# Add new writing
./scripts/add-writing.py

# Review changes
git diff

# Commit and push
git add .
git commit -m "Add new content"
git push
```

## Customization Tips

### Change Color Scheme

Edit `assets/css/style.css`, lines 9-21 (light mode) and 33-45 (dark mode):

```css
:root {
    --link-color: #00e;  /* Change link color */
    --bg-primary: #fff;  /* Change background */
}
```

### Add New Navigation Section

In each HTML file's `<nav id="sidenav">`:

```html
<section class="nav-section">
    <h2>Your Section</h2>
    <ul>
        <li><a href="your-page.html">Page Name</a></li>
    </ul>
</section>
```

### Modify Typography

Edit `assets/css/style.css`, lines 23-25:

```css
--font-serif: 'Your Font', 'Fallback', serif;
--font-sans: 'Your Sans Font', sans-serif;
```

## Common Tasks

### Update "Last Modified" Dates

Find and update `<time>` elements:
```html
<time datetime="2025-12-15">15 December 2025</time>
```

### Add New Page Type

1. Copy an existing page as template
2. Create a new script in `scripts/` (use existing scripts as reference)
3. Update navigation in all pages
4. Document in README

### Link to Definitions

Use this format in your writing:
```html
<a href="pages/definitions.html#term-slug" 
   class="definition-link" 
   data-term="Term Name" 
   data-definition="Brief hover text">Term Name</a>
```

## Troubleshooting

**Scripts won't run:**
```bash
# Make executable
chmod +x scripts/*.py

# Run with python3 explicitly
python3 scripts/add-quote.py
```

**Changes not showing on GitHub Pages:**
- Wait 2-5 minutes for build
- Check Actions tab for errors
- Clear browser cache (Cmd+Shift+R / Ctrl+Shift+R)

**Dark mode not working:**
- Check JavaScript console for errors
- Ensure localStorage is enabled in browser
- Try: `localStorage.clear()` in console

## Resources

- **Full documentation**: See `README.md`
- **GitHub Pages docs**: https://docs.github.com/pages
- **Gwern.net** (inspiration): https://gwern.net
- **Markdown guide** (for README): https://www.markdownguide.org/

## Next Steps

1. ✓ Customize identity and contact info
2. ✓ Test locally
3. ✓ Add your first piece of content
4. ✓ Deploy to GitHub Pages
5. → Start writing and building your knowledge base!

---

**Need help?** Check the full README.md or open an issue on GitHub.
