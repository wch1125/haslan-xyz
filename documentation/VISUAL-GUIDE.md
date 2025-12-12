# H. Aslan Wiki - Visual Quick Reference

## 📁 Your Complete Wiki Package

```
has-lan-wiki/
│
├── 📄 index.html                    ← Your homepage
├── 📄 robots.txt                    ← Blocks AI scrapers
├── 📄 CNAME                         ← Custom domain (optional)
├── 📄 .gitignore                    ← Git configuration
│
├── 📚 Documentation
│   ├── README.md                    ← Full documentation (9.5 KB)
│   ├── QUICKSTART.md                ← Quick start guide (4.3 KB)
│   ├── DEPLOYMENT.md                ← Deploy to GitHub Pages (9.8 KB)
│   └── IMPROVEMENTS.md              ← What's new/improved (8.4 KB)
│
├── 🎨 assets/
│   ├── css/
│   │   └── style.css                ← All styling, Gwern-inspired
│   └── js/
│       └── script.js                ← Enhanced with definition popups
│
├── 📝 pages/
│   ├── quotes.html                  ← Quote collection + filtering
│   ├── definitions.html             ← Glossary with hover previews ✨
│   ├── creative-writing.html        ← Writing index
│   ├── contact.html                 ← Contact page (UPDATE THIS!)
│   ├── demo.html                    ← Feature demonstration
│   └── writing/                     ← Individual writing pieces
│       └── .gitkeep
│
└── 🤖 scripts/
    ├── add-quote.py                 ← Automate adding quotes
    ├── add-definition.py            ← Automate adding definitions
    └── add-writing.py               ← Automate adding writing
```

## 🚀 Quick Start in 3 Steps

### Step 1: Customize (5 min)
```bash
# Update contact info
vim pages/contact.html

# Optional: Change pseudonym
sed -i 's/H. Aslan/YourName/g' **/*.html
```

### Step 2: Test (2 min)
```bash
python3 -m http.server 8000
# Visit http://localhost:8000
```

### Step 3: Deploy (5 min)
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOU/REPO.git
git push -u origin main

# Enable GitHub Pages: Settings → Pages → main → / (root) → Save
# Live at: https://YOU.github.io/REPO/
```

## 📝 Adding Content (No HTML!)

### Add a Quote
```bash
$ python3 scripts/add-quote.py

Enter quote text: [Your quote]
Author: [Name]
Source: [Book/Article]
Year: [YYYY]
Tags: creativity,art,observation

✓ Added to pages/quotes.html
```

### Add a Definition
```bash
$ python3 scripts/add-definition.py

Term name: Empathy
Definition: [Your definition]
Related terms: authenticity,observation

✓ Added to pages/definitions.html
```

### Add Writing
```bash
$ python3 scripts/add-writing.py

Title: [Title]
Category: Short Story
Excerpt: [Brief description]
Content: [Your text]
END

✓ Created pages/writing/your-slug.html
✓ Updated pages/creative-writing.html
```

## 🎨 Key Features

### 1️⃣ Definition Hover System
```html
<a href="pages/definitions.html#empathy" 
   class="definition-link" 
   data-term="Empathy" 
   data-definition="Brief popup text">Empathy</a>
```
→ **Desktop**: Hover shows preview
→ **Click**: Goes to full definition

### 2️⃣ Sidenotes (Tufte-style)
```html
<p>Main text<span class="sidenote">
    <span class="sidenote-number"></span>
    <span class="sidenote-content">Margin note here</span>
</span> continuing.</p>
```
→ **Desktop**: Appears in margin
→ **Mobile**: Converts to inline

### 3️⃣ Dropcaps
```html
<p><span class="dropcap">T</span>his looks elegant.</p>
```

### 4️⃣ Collapsible Sections
```html
<details class="collapse">
    <summary>Click to expand</summary>
    <div class="collapse-content">
        <p>Hidden content</p>
    </div>
</details>
```
→ State persists between visits

### 5️⃣ Dark Mode
- **Button**: In sidebar
- **Keyboard**: Alt+D
- **Persistence**: LocalStorage

### 6️⃣ Link Popups
```javascript
// Edit assets/js/script.js
excerpts: {
    'pages/new-page.html': {
        title: 'Page Title',
        text: 'Preview text...'
    }
}
```

## 🎯 File You'll Edit Most

| File | How | Frequency |
|------|-----|-----------|
| `pages/quotes.html` | Via script | Often |
| `pages/definitions.html` | Via script | Often |
| `pages/creative-writing.html` | Via script | Often |
| `pages/contact.html` | Manual | Once |
| `index.html` | Manual | Rarely |
| `assets/css/style.css` | Manual | If customizing |

## 🔧 Common Customizations

### Change Colors
Edit `assets/css/style.css` lines 9-45:
```css
:root {
    --link-color: #00e;  /* Change this */
    --bg-primary: #fff;  /* And this */
}
```

### Add Navigation Section
In all HTML files, add to `<nav id="sidenav">`:
```html
<section class="nav-section">
    <h2>New Section</h2>
    <ul>
        <li><a href="page.html">Link</a></li>
    </ul>
</section>
```

### Change Fonts
Edit `assets/css/style.css` lines 23-25:
```css
--font-serif: 'Your Font', serif;
--font-sans: 'Your Sans', sans-serif;
```

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Alt + D` | Toggle dark mode |
| `Alt + H` | Go to homepage |

Add more in `assets/js/script.js` lines 180-194

## 🐛 Troubleshooting

**Scripts won't run?**
```bash
chmod +x scripts/*.py
# or
python3 scripts/add-quote.py
```

**GitHub Pages not updating?**
- Wait 5 minutes
- Check Actions tab
- Clear browser cache (Cmd/Ctrl + Shift + R)

**Popups not working?**
- Desktop only (hover required)
- Check browser console
- Verify excerpts in script.js

## 📊 What's Fixed/Improved

✅ Changed W. Haslun → H. Aslan throughout
✅ Fixed Definitions page (removed Quote artifacts)
✅ Added definition hover system with CSS
✅ Created automation scripts (no more line-by-line HTML!)
✅ Reorganized file structure
✅ Enhanced JavaScript functionality
✅ Comprehensive documentation (4 guides)
✅ GitHub Pages ready
✅ Mobile responsive
✅ Dark mode with keyboard shortcut

## 🎓 Learning Resources

**Included Documentation:**
1. `README.md` - Comprehensive guide
2. `QUICKSTART.md` - Get started fast
3. `DEPLOYMENT.md` - Deploy to web
4. `IMPROVEMENTS.md` - What's new

**External Resources:**
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [Markdown Guide](https://www.markdownguide.org/)
- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)
- [Gwern.net](https://gwern.net) (design inspiration)

## 💡 Pro Tips

1. **Commit often**: Small, frequent commits are better
2. **Test locally first**: Always test before pushing
3. **Use the scripts**: They prevent formatting errors
4. **Document changes**: Good commit messages help later
5. **Back up content**: Git is your friend

## 🎉 You're Ready!

Your wiki has:
- ✅ Professional design
- ✅ Advanced features
- ✅ Automation tools
- ✅ Complete docs
- ✅ GitHub ready

**Next step**: Update contact info and deploy!

---

**Questions?** Check the full README.md
**Problems?** See DEPLOYMENT.md troubleshooting
**Ideas?** The code is yours to modify!

Last updated: December 8, 2025
