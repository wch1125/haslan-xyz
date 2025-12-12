# H. Aslan Wiki - Deployment & Usage Guide

## What You Have

A complete, GitHub-ready personal wiki with:

✓ Gwern-inspired design with dark mode
✓ Advanced typography (dropcaps, sidenotes, smallcaps)
✓ Interactive features (link popups, collapsible sections)
✓ Hover-enabled definition system
✓ Automated content management (Python scripts)
✓ Fully responsive design
✓ Zero dependencies

## File Structure

```
has-lan-wiki/
├── index.html                    # Homepage
├── README.md                     # Full documentation
├── QUICKSTART.md                 # Quick start guide
├── CNAME                         # Custom domain config (optional)
├── robots.txt                    # Search engine directives
├── .gitignore                    # Git ignore rules
│
├── assets/
│   ├── css/
│   │   └── style.css            # All styling (updated with H. Aslan branding)
│   └── js/
│       └── script.js            # Enhanced JavaScript with definition popups
│
├── pages/
│   ├── quotes.html              # Quotes collection with filtering
│   ├── definitions.html         # Glossary with hover previews (FIXED)
│   ├── creative-writing.html    # Writing index
│   ├── contact.html             # Contact page (customize this!)
│   ├── demo.html                # Feature demonstration
│   └── writing/                 # Individual writing pieces go here
│       └── .gitkeep
│
└── scripts/
    ├── add-quote.py             # Automate adding quotes
    ├── add-definition.py        # Automate adding definitions
    └── add-writing.py           # Automate adding writing pieces
```

## Immediate Action Items

### 1. Update Contact Information (REQUIRED)

Edit `pages/contact.html`:
- Line 52: Replace `your.email@example.com` with your actual email
- Lines 56-58: Add your social media links
- Customize the rest as needed

### 2. Choose Your Pseudonym

The site currently uses "H. Aslan" throughout. To change it:

**Option A - Manual:**
1. Search and replace "H. Aslan" in all HTML files
2. Update the console message in `assets/js/script.js` line 362

**Option B - Command line (recommended):**
```bash
# macOS/BSD
find . -type f -name "*.html" -exec sed -i '' 's/H. Aslan/YourName/g' {} +
sed -i '' 's/H. Aslan/YourName/g' assets/js/script.js

# Linux
find . -type f -name "*.html" -exec sed -i 's/H. Aslan/YourName/g' {} +
sed -i 's/H. Aslan/YourName/g' assets/js/script.js
```

### 3. Test Locally

```bash
cd has-lan-wiki
python3 -m http.server 8000
# Visit http://localhost:8000
```

Test these features:
- Dark mode toggle (Alt+D or button in sidebar)
- Navigation between pages
- Hover over links in demo.html to see popups
- Hover over definition links in definitions.html
- Mobile responsive design (resize browser)

## Deploying to GitHub Pages

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `has-lan-wiki` (or your preferred name)
3. Keep it Public (required for free GitHub Pages)
4. Don't initialize with README (you already have one)
5. Click "Create repository"

### Step 2: Push Your Code

```bash
cd has-lan-wiki

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: H. Aslan personal wiki"

# Connect to GitHub (replace with your URL from Step 1)
git remote add origin https://github.com/YOUR-USERNAME/has-lan-wiki.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click "Settings" → "Pages" (in left sidebar)
3. Under "Source", select:
   - Branch: `main`
   - Folder: `/ (root)`
4. Click "Save"
5. Wait 2-5 minutes

Your site will be live at: `https://YOUR-USERNAME.github.io/has-lan-wiki/`

### Step 4 (Optional): Custom Domain

If you have a custom domain (e.g., haslan.com):

1. Edit the `CNAME` file in the root:
   ```
   yourdomain.com
   ```

2. Configure DNS with your domain provider:
   - Add a CNAME record: `www` → `YOUR-USERNAME.github.io`
   - Or A records pointing to GitHub's IPs (see [GitHub docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site))

3. Commit and push the CNAME file:
   ```bash
   git add CNAME
   git commit -m "Add custom domain"
   git push
   ```

## Using the Automation Scripts

### Adding Quotes

```bash
python3 scripts/add-quote.py
```

Follow the prompts:
1. Enter quote text (can be multiple lines, press Enter twice when done)
2. Author name
3. Source (book title, article name, etc.)
4. Year (optional)
5. Tags (comma-separated: `creativity,art,observation`)

The script will:
- Format the quote properly
- Add it to the top of `pages/quotes.html`
- Include tags for filtering
- Add timestamp

### Adding Definitions

```bash
python3 scripts/add-definition.py
```

Follow the prompts:
1. Term name (e.g., "Empathy")
2. Definition paragraphs (press Enter twice when done)
3. Related terms (optional, comma-separated)

The script will:
- Create a properly formatted definition entry
- Add it to `pages/definitions.html`
- Generate the URL slug automatically
- Set up alphabetical indexing

**Using Definitions in Your Writing:**

When you want to reference a defined term with hover preview:

```html
<a href="pages/definitions.html#empathy" 
   class="definition-link" 
   data-term="Empathy" 
   data-definition="The capacity to model another person's emotional state through observation and pattern recognition.">Empathy</a>
```

### Adding Creative Writing

```bash
python3 scripts/add-writing.py
```

Follow the prompts:
1. Title
2. Category (Short Story, Poem, Essay, Fragment, etc.)
3. Brief excerpt (1-2 sentences for the index)
4. Content (type 'END' on a new line when finished)

The script will:
- Create a new HTML page in `pages/writing/`
- Add an entry to the creative writing index
- Set up proper navigation
- Include metadata

## Daily Workflow

### Making Updates

```bash
# Option 1: Use scripts (recommended for quotes, definitions, writing)
python3 scripts/add-quote.py
# ... make edits ...
git add .
git commit -m "Add new quote about observation"
git push

# Option 2: Edit HTML directly (for quick tweaks)
# Edit the file in your favorite editor
git add pages/quotes.html
git commit -m "Update quote formatting"
git push
```

### GitHub Pages will automatically rebuild (takes 2-5 minutes)

## Key Features Explained

### Definition System

The Definitions page (`pages/definitions.html`) has been **fixed** from the original code. It now:
- Uses proper structure (no Quote artifacts)
- Supports hover previews via `definition-link` class
- Links from anywhere in the site
- Example definitions included (Authenticity, Conformity, Empathy)

**How to use:**
1. Add definitions using the script or manually
2. Reference them in your writing with the special link format
3. Users hover to see a preview, click to read the full definition

### Link Popups

Internal page links show previews on hover (desktop only). To add a new page to the preview system:

Edit `assets/js/script.js`, add to the `excerpts` object:

```javascript
'pages/your-new-page.html': {
    title: 'Page Title',
    text: 'Brief description that appears in the popup...'
}
```

### Sidenotes

```html
<p>Text with a sidenote<span class="sidenote">
    <span class="sidenote-number"></span>
    <span class="sidenote-content">This appears in the margin on desktop, inline on mobile.</span>
</span> continuing.</p>
```

Auto-numbers and positions in margin on desktop, converts to inline on mobile.

### Dark Mode

- Toggle with Alt+D keyboard shortcut
- Or click button in sidebar
- Preference saved in localStorage
- Smooth transitions between themes

## Troubleshooting

**Scripts not running:**
```bash
# Make executable
chmod +x scripts/*.py

# Or run with python3 explicitly
python3 scripts/add-quote.py
```

**GitHub Pages not updating:**
- Check the "Actions" tab on GitHub for build status
- Wait 5 minutes (GitHub Pages can be slow)
- Clear browser cache (Cmd/Ctrl + Shift + R)

**Link popups not working:**
- Only work on desktop (hover-capable devices)
- Check browser console for JavaScript errors
- Verify the page is in the `excerpts` object in `script.js`

**Definition hovers not working:**
- Check that you're using `class="definition-link"`
- Verify `data-term` and `data-definition` attributes are set
- Only works on desktop with hover capability

## What's Been Fixed

From your original code:

1. ✓ Changed all "W. Haslun" references to "H. Aslan"
2. ✓ Fixed Definitions page (removed Quote page artifacts)
3. ✓ Added definition hover system with proper CSS
4. ✓ Reorganized file structure for clarity
5. ✓ Updated all relative paths for new structure
6. ✓ Added automation scripts for content management
7. ✓ Created comprehensive documentation

## Next Steps

1. **Customize contact info** in `pages/contact.html`
2. **Change pseudonym** if desired (see instructions above)
3. **Test locally** to ensure everything works
4. **Deploy to GitHub** following the steps above
5. **Add your first content** using the scripts
6. **Start building** your knowledge base!

## Resources

- **Full README**: See `README.md` for comprehensive documentation
- **Quick Start**: See `QUICKSTART.md` for rapid setup
- **GitHub Pages**: https://docs.github.com/en/pages
- **Git Basics**: https://git-scm.com/book/en/v2/Getting-Started-Git-Basics

## Support

The code is well-commented and structured. If you need to modify something:

1. Check the relevant section in `README.md`
2. Look at the existing code structure
3. The automation scripts show how to add content programmatically
4. All CSS is in one file: `assets/css/style.css`
5. All JavaScript is in one file: `assets/js/script.js`

---

**You're all set!** This is a complete, production-ready personal wiki system.

Last updated: December 8, 2025
