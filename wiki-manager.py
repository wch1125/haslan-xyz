#!/usr/bin/env python3
"""
H. Aslan Wiki Manager
A local web interface for adding content to your wiki.

SETUP:
    pip install flask

USAGE:
    python wiki-manager.py
    Then open http://localhost:5000 in your browser

The app writes directly to your HTML files. After adding content,
commit and push to deploy:
    git add . && git commit -m "Add new content" && git push
"""

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, redirect, url_for

app = Flask(__name__)

# Get the directory where this script lives (your wiki root)
WIKI_ROOT = Path(__file__).parent.resolve()
PAGES_DIR = WIKI_ROOT / "pages"
WRITING_DIR = PAGES_DIR / "writing"

# ============================================
# UTILITY FUNCTIONS
# ============================================

def slugify(text):
    """Convert text to URL-friendly slug"""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def parse_related_token(raw):
    """
    Parse related term tokens that may include annotations.
    Supports:
      - "Term"
      - "Term|note" (e.g., "Conformity|opposite")
    Returns (term, note) tuple with whitespace trimmed.
    """
    raw = (raw or "").strip()
    if not raw:
        return None, None

    if "|" in raw:
        term, note = [p.strip() for p in raw.split("|", 1)]
    else:
        term, note = raw, ""

    term = term.strip()
    if not term:
        return None, None

    return term, note

def get_current_date():
    """Get current date in various formats"""
    now = datetime.now()
    return {
        'iso': now.strftime('%Y-%m-%d'),
        'display': now.strftime('%d %B %Y'),
        'month_year': now.strftime('%B %Y')
    }

def git_status():
    """Check if there are uncommitted changes"""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=WIKI_ROOT,
            capture_output=True,
            text=True
        )
        return len(result.stdout.strip()) > 0
    except:
        return False

def git_commit_and_push(message):
    """Commit all changes and push"""
    try:
        subprocess.run(['git', 'add', '.'], cwd=WIKI_ROOT, check=True)
        subprocess.run(['git', 'commit', '-m', message], cwd=WIKI_ROOT, check=True)
        subprocess.run(['git', 'push'], cwd=WIKI_ROOT, check=True)
        return True, "Changes committed and pushed successfully!"
    except subprocess.CalledProcessError as e:
        return False, f"Git error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

# ============================================
# CONTENT INSERTION FUNCTIONS
# ============================================

def add_quote(quote_text, author, source, year, tags):
    """Add a quote to quotes.html"""
    dates = get_current_date()
    tags_list = [t.strip().lower() for t in tags.split(',') if t.strip()]
    
    tags_html = '\n                            '.join(
        f'<span class="quote-tag">{tag}</span>' for tag in tags_list
    )
    
    source_display = f"{source} ({year})" if year else source
    
    quote_html = f'''
                <div class="quote-entry" data-tags="{','.join(tags_list)}" data-date="{dates['iso']}">
                    <blockquote class="quote-text">
                        {quote_text}
                    </blockquote>
                    <div class="quote-attribution">
                        <span class="quote-author">{author}</span>
                        <span class="quote-source">{source_display}</span>
                    </div>
                    <div class="quote-metadata">
                        <div class="quote-tags">
                            {tags_html}
                        </div>
                        <time class="quote-date" datetime="{dates['iso']}">Added {dates['month_year']}</time>
                    </div>
                </div>
'''
    
    quotes_file = PAGES_DIR / "quotes.html"
    with open(quotes_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Insert after <h2>Quotes</h2>
    marker = '<h2>Quotes</h2>'
    if marker in content:
        insert_pos = content.find(marker) + len(marker)
        new_content = content[:insert_pos] + quote_html + content[insert_pos:]
        
        with open(quotes_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def add_definition(term, definition_paragraphs, related_terms):
    """Add a definition to definitions.html"""
    dates = get_current_date()
    slug = slugify(term)
    letter = term[0].upper()
    
    # Format paragraphs
    paragraphs_html = '\n                        '.join(
        f'<p>{p.strip()}</p>' for p in definition_paragraphs if p.strip()
    )
    
    # Related terms section
    related_html = ''
    if related_terms:
        related_list = [t.strip() for t in related_terms.split(',') if t.strip()]
        if related_list:
            parsed = [parse_related_token(t) for t in related_list]
            related_items = '\n                                    '.join(
                f'<li><a href="#{slugify(term)}">{term}</a>'
                f'{f" <span class=\"related-note\">({note})</span>" if note else ""}'
                f'</li>'
                for term, note in parsed
                if term
            )
            related_html = f'''
                        <details class="collapse">
                            <summary>Related Concepts</summary>
                            <div class="collapse-content">
                                <ul>
                                    {related_items}
                                </ul>
                            </div>
                        </details>'''
    
    definition_html = f'''
                <div class="definition-entry" id="{slug}">
                    <h3><span class="definition-term">{term}</span></h3>
                    <div class="definition-metadata">
                        <span class="definition-letter">{letter}</span>
                        <span class="definition-date">Added: {dates['month_year']}</span>
                    </div>
                    <div class="definition-content">
                        {paragraphs_html}{related_html}
                    </div>
                </div>
'''
    
    definitions_file = PAGES_DIR / "definitions.html"
    with open(definitions_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Insert before the template comment
    marker = '<!-- Template for new definitions'
    if marker in content:
        insert_pos = content.find(marker)
        new_content = content[:insert_pos] + definition_html + '\n' + content[insert_pos:]
        
        with open(definitions_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, slug
    return False, None

def add_writing(title, category, excerpt, content_text):
    """Add a writing piece - creates new file and updates index"""
    dates = get_current_date()
    slug = slugify(title)
    filename = f"{slug}.html"
    
    # Create the writing page
    writing_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} • H. Aslan</title>
    <meta name="description" content="{excerpt}">
    <link rel="stylesheet" href="../../assets/css/style.css">
</head>
<body>
    <nav id="sidenav">
        <div class="nav-header">
            <h1><a href="../../index.html">H. Aslan</a></h1>
            <p class="tagline">Notes from the margins</p>
        </div>
        
        <section class="nav-section">
            <h2>Topics</h2>
            <ul>
                <li><a href="../creative-writing.html">Creative Writing</a></li>
                <li><a href="../quotes.html">Quotes</a></li>
                <li><a href="../definitions.html">Definitions</a></li>
                <li><a href="../personal-domain.html">Personal Domain</a></li>
                <li><a href="../demo.html">Demo</a></li>
            </ul>
        </section>

        <section class="nav-section">
            <h2>Connect</h2>
            <ul>
                <li><a href="../contact.html">Contact</a></li>
            </ul>
        </section>
        
        <div class="theme-toggle">
            <button id="theme-toggle-btn" aria-label="Toggle dark mode">
                <span class="sun">☀</span>
                <span class="moon">☾</span>
            </button>
        </div>
    </nav>

    <main id="content">
        <article>
            <a href="../creative-writing.html" class="back-link">Back to Creative Writing</a>
            
            <header class="page-header">
                <h1>{title}</h1>
                <div class="page-metadata">
                    <span class="writing-category">{category}</span>
                    <time datetime="{dates['iso']}">{dates['display']}</time>
                </div>
            </header>

            <section class="writing-content">
                {content_text}
            </section>
        </article>
    </main>

    <script src="../../assets/js/script.js"></script>
</body>
</html>
'''
    
    # Write the new file
    WRITING_DIR.mkdir(exist_ok=True)
    writing_file = WRITING_DIR / filename
    with open(writing_file, 'w', encoding='utf-8') as f:
        f.write(writing_html)
    
    # Add entry to creative-writing.html index
    index_entry = f'''
                    <div class="writing-card" data-category="{category.lower()}">
                        <h3><a href="writing/{filename}">{title}</a></h3>
                        <div class="writing-metadata">
                            <span class="writing-category">{category}</span>
                            <time datetime="{dates['iso']}">{dates['display']}</time>
                        </div>
                        <p class="writing-excerpt">{excerpt}</p>
                    </div>
'''
    
    index_file = PAGES_DIR / "creative-writing.html"
    with open(index_file, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    # Insert after <div class="writing-grid">
    marker = '<div class="writing-grid">'
    if marker in index_content:
        insert_pos = index_content.find(marker) + len(marker)
        new_content = index_content[:insert_pos] + index_entry + index_content[insert_pos:]
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, filename
    return False, None

def add_page(title, filename_or_slug, description, abstract, content_html, add_to_home=False):
    """Create a non-writing page in /pages and optionally add a homepage card."""
    dates = get_current_date()

    base = (filename_or_slug or title or "").strip()
    base = re.sub(r'\.html?$', '', base, flags=re.IGNORECASE).strip()
    if not base:
        base = title.strip()

    slug = slugify(base)
    filename = f"{slug}.html"

    # Basic fallbacks
    meta_description = (description or abstract or "").strip()

    # Page template (mirrors /pages/* structure)
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} • H. Aslan</title>
  <meta name="description" content="{meta_description}">
  <link rel="stylesheet" href="../assets/css/style.css" />
</head>

<body>
  <nav id="sidenav">
    <div class="nav-header">
      <h1><a href="../index.html">H. Aslan</a></h1>
      <p class="tagline">Notes from the margins</p>
    </div>

    <section class="nav-section">
      <h2>Topics</h2>
      <ul>
        <li><a href="creative-writing.html">Creative Writing</a></li>
        <li><a href="quotes.html">Quotes</a></li>
        <li><a href="definitions.html">Definitions</a></li>
        <li><a href="personal-domain.html">Personal Domain</a></li>
        <li><a href="demo.html">Demo</a></li>
      </ul>
    </section>

    <section class="nav-section">
      <h2>Connect</h2>
      <ul>
        <li><a href="contact.html">Contact</a></li>
      </ul>
    </section>

    <div class="theme-toggle">
      <button id="theme-toggle-btn" aria-label="Toggle dark mode">
        <span class="sun">☀</span>
        <span class="moon">☾</span>
      </button>
    </div>
  </nav>

  <main id="content">
    <article>
      <a href="../index.html" class="back-link">Back to Home</a>

      <header class="page-header">
        <h1>{title}</h1>
        <div class="page-metadata">
          <time datetime="{dates['iso']}">{dates['display']}</time>
        </div>
      </header>

      {"<div class='abstract'><p><span class='abstract-label'>Abstract:</span> " + abstract + "</p></div>" if (abstract or "").strip() else ""}

      {content_html}
    </article>
  </main>

  <script src="../assets/js/script.js"></script>
</body>
</html>
"""

    PAGES_DIR.mkdir(exist_ok=True)
    page_file = PAGES_DIR / filename
    with open(page_file, "w", encoding="utf-8") as f:
        f.write(page_html)

    # Optionally add a card to the homepage grid
    added_to_home = False
    if add_to_home:
        home_file = WIKI_ROOT / "index.html"
        with open(home_file, "r", encoding="utf-8") as f:
            home = f.read()

        marker = '<div class="topic-grid">'
        if marker in home:
            blurb = (description or abstract or "").strip()
            if not blurb:
                blurb = "—"

            card_html = f'''
                    <div class="topic-card">
                        <h3><a href="pages/{filename}">{title}</a></h3>
                        <p>{blurb}</p>
                    </div>
'''

            insert_pos = home.find(marker) + len(marker)
            home_new = home[:insert_pos] + card_html + home[insert_pos:]
            with open(home_file, "w", encoding="utf-8") as f:
                f.write(home_new)

            added_to_home = True

    return True, filename, added_to_home

# ============================================
# HTML TEMPLATE
# ============================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>H. Aslan Wiki Manager</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Georgia', serif; }
        .tab-active { border-bottom: 3px solid #b8860b; color: #b8860b; }
        textarea { font-family: 'Georgia', serif; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="max-w-3xl mx-auto px-4 py-8">
        <!-- Header -->
        <div class="mb-8 text-center">
            <h1 class="text-3xl font-serif italic text-gray-800 mb-2">H. Aslan Wiki Manager</h1>
            <p class="text-gray-500">Add content to your wiki at haslan.xyz</p>
        </div>

        <!-- Flash Messages -->
        {% if message %}
        <div class="mb-6 p-4 rounded {{ 'success' if success else 'error' }}">
            {{ message }}
        </div>
        {% endif %}

        <!-- Tabs -->
        <div class="border-b border-gray-200 mb-6">
            <nav class="flex space-x-8">
                <a href="?tab=quote" class="py-3 px-1 text-sm font-medium {{ 'tab-active' if tab == 'quote' else 'text-gray-500 hover:text-gray-700' }}">
                    Add Quote
                </a>
                <a href="?tab=definition" class="py-3 px-1 text-sm font-medium {{ 'tab-active' if tab == 'definition' else 'text-gray-500 hover:text-gray-700' }}">
                    Add Definition
                </a>
                <a href="?tab=writing" class="py-3 px-1 text-sm font-medium {{ 'tab-active' if tab == 'writing' else 'text-gray-500 hover:text-gray-700' }}">
                    Add Writing
                </a>
                <a href="?tab=page" class="py-3 px-1 text-sm font-medium {{ 'tab-active' if tab == 'page' else 'text-gray-500 hover:text-gray-700' }}">
                    Add Page
                </a>
                <a href="?tab=deploy" class="py-3 px-1 text-sm font-medium {{ 'tab-active' if tab == 'deploy' else 'text-gray-500 hover:text-gray-700' }}">
                    Deploy
                </a>
            </nav>
        </div>

        <!-- Quote Form -->
        {% if tab == 'quote' %}
        <form method="POST" action="/add-quote" class="space-y-6">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Quote Text</label>
                <textarea name="quote_text" rows="4" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    placeholder="Enter the quote text..."></textarea>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Author</label>
                    <input type="text" name="author" required
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                        placeholder="e.g., Joan Didion">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Source</label>
                    <input type="text" name="source" required
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                        placeholder="e.g., Slouching Towards Bethlehem">
                </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Year (optional)</label>
                    <input type="text" name="year"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                        placeholder="e.g., 1968">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Tags (comma-separated)</label>
                    <input type="text" name="tags" required
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                        placeholder="e.g., writing, creativity, observation">
                </div>
            </div>
            <button type="submit" 
                class="w-full py-3 px-4 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-md transition">
                Add Quote
            </button>
        </form>
        {% endif %}

        <!-- Definition Form -->
        {% if tab == 'definition' %}
        <form method="POST" action="/add-definition" class="space-y-6">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Term</label>
                <input type="text" name="term" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="e.g., Authenticity">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Definition</label>
                <p class="text-xs text-gray-500 mb-2">Separate paragraphs with blank lines</p>
                <textarea name="definition" rows="6" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="First paragraph of definition...

Second paragraph if needed..."></textarea>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Related Terms (optional, comma-separated; use Term|note for annotations)</label>
                <input type="text" name="related"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="e.g., Integrity, Conformity|opposite, Authenticity|adjacent">
            </div>
            <button type="submit" 
                class="w-full py-3 px-4 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-md transition">
                Add Definition
            </button>
        </form>
        {% endif %}

        <!-- Writing Form -->
        {% if tab == 'writing' %}
        <form method="POST" action="/add-writing" class="space-y-6">
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Title</label>
                    <input type="text" name="title" required
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                        placeholder="e.g., On Walking at Night">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
                    <select name="category" required
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500">
                        <option value="Essay">Essay</option>
                        <option value="Fragment">Fragment</option>
                        <option value="Poem">Poem</option>
                        <option value="Short Story">Short Story</option>
                        <option value="Observation">Observation</option>
                        <option value="Analysis">Analysis</option>
                    </select>
                </div>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Excerpt (for index page)</label>
                <input type="text" name="excerpt" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="A brief description that appears on the writing index...">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Content</label>
                <p class="text-xs text-gray-500 mb-2">You can use HTML tags: &lt;p&gt;, &lt;em&gt;, &lt;strong&gt;, &lt;blockquote&gt;</p>
                <textarea name="content" rows="12" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500 font-mono text-sm"
                    placeholder="<p>First paragraph...</p>

<p>Second paragraph...</p>"></textarea>
            </div>
            <button type="submit" 
                class="w-full py-3 px-4 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-md transition">
                Add Writing
            </button>
        </form>
        {% endif %}

        <!-- Page Form -->
        {% if tab == 'page' %}
        <form method="POST" action="/add-page" class="space-y-6">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Title</label>
                <input type="text" name="title" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="e.g., Personal Domains and Narrative Sovereignty">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Filename/Slug (optional)</label>
                <input type="text" name="filename"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="e.g., personal-domain (auto-generated from title if blank)">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Description (optional, for meta and homepage card)</label>
                <input type="text" name="description"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="Short blurb for meta/home card">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Abstract (optional, appears on page)</label>
                <textarea name="abstract" rows="3"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="If provided, appears as the on-page Abstract block."></textarea>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Content (HTML)</label>
                <p class="text-xs text-gray-500 mb-2">You can paste full sections. This gets inserted into the page body.</p>
                <textarea name="content" rows="12" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500 font-mono text-sm"
                    placeholder="<section id=&quot;intro&quot;>
  <p>Your content here...</p>
</section>"></textarea>
            </div>

            <div class="flex items-center gap-2">
                <input type="checkbox" name="add_to_home" id="add_to_home"
                    class="h-4 w-4">
                <label for="add_to_home" class="text-sm text-gray-700">Also add a card to the homepage</label>
            </div>

            <button type="submit"
                class="w-full py-3 px-4 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-md transition">
                Create Page
            </button>
        </form>
        {% endif %}

        <!-- Deploy Tab -->
        {% if tab == 'deploy' %}
        <div class="space-y-6">
            <div class="bg-white p-6 rounded-lg border border-gray-200">
                <h3 class="text-lg font-medium text-gray-800 mb-4">Deploy Changes</h3>
                <p class="text-gray-600 mb-4">
                    {% if has_changes %}
                    You have uncommitted changes. Click below to commit and push to GitHub.
                    {% else %}
                    No uncommitted changes detected.
                    {% endif %}
                </p>
                <form method="POST" action="/deploy" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Commit Message</label>
                        <input type="text" name="commit_message" required
                            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                            placeholder="e.g., Add new quote about observation"
                            value="Update wiki content">
                    </div>
                    <button type="submit" 
                        class="w-full py-3 px-4 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition"
                        {% if not has_changes %}disabled class="opacity-50 cursor-not-allowed"{% endif %}>
                        Commit & Push to GitHub
                    </button>
                </form>
            </div>

            <div class="bg-gray-100 p-6 rounded-lg">
                <h3 class="text-lg font-medium text-gray-800 mb-2">Manual Deploy</h3>
                <p class="text-gray-600 mb-3">Or run these commands in your terminal:</p>
                <pre class="bg-gray-800 text-green-400 p-4 rounded text-sm overflow-x-auto">cd {{ wiki_root }}
git add .
git commit -m "Update wiki content"
git push</pre>
            </div>
        </div>
        {% endif %}

        <!-- Footer -->
        <div class="mt-12 pt-6 border-t border-gray-200 text-center text-sm text-gray-500">
            <p>Wiki location: <code class="bg-gray-100 px-2 py-1 rounded">{{ wiki_root }}</code></p>
            <p class="mt-2">
                <a href="http://localhost:5000" class="text-amber-600 hover:underline">Refresh</a> · 
                <a href="file://{{ wiki_root }}/index.html" class="text-amber-600 hover:underline">Preview locally</a>
            </p>
        </div>
    </div>
</body>
</html>
'''

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    tab = request.args.get('tab', 'quote')
    message = request.args.get('message')
    success = request.args.get('success', 'true') == 'true'
    
    return render_template_string(
        HTML_TEMPLATE,
        tab=tab,
        message=message,
        success=success,
        has_changes=git_status(),
        wiki_root=str(WIKI_ROOT)
    )

@app.route('/add-quote', methods=['POST'])
def handle_add_quote():
    try:
        success = add_quote(
            quote_text=request.form['quote_text'],
            author=request.form['author'],
            source=request.form['source'],
            year=request.form.get('year', ''),
            tags=request.form['tags']
        )
        if success:
            return redirect(url_for('index', tab='quote', message='Quote added successfully!', success='true'))
        else:
            return redirect(url_for('index', tab='quote', message='Error: Could not find insertion point in quotes.html', success='false'))
    except Exception as e:
        return redirect(url_for('index', tab='quote', message=f'Error: {e}', success='false'))

@app.route('/add-definition', methods=['POST'])
def handle_add_definition():
    try:
        paragraphs = [p.strip() for p in request.form['definition'].split('\n\n') if p.strip()]
        success, slug = add_definition(
            term=request.form['term'],
            definition_paragraphs=paragraphs,
            related_terms=request.form.get('related', '')
        )
        if success:
            return redirect(url_for('index', tab='definition', message=f'Definition added! Slug: #{slug}', success='true'))
        else:
            return redirect(url_for('index', tab='definition', message='Error: Could not find insertion point', success='false'))
    except Exception as e:
        return redirect(url_for('index', tab='definition', message=f'Error: {e}', success='false'))

@app.route('/add-writing', methods=['POST'])
def handle_add_writing():
    try:
        success, filename = add_writing(
            title=request.form['title'],
            category=request.form['category'],
            excerpt=request.form['excerpt'],
            content_text=request.form['content']
        )
        if success:
            return redirect(url_for('index', tab='writing', message=f'Writing added! File: {filename}', success='true'))
        else:
            return redirect(url_for('index', tab='writing', message='Error: Could not update index', success='false'))
    except Exception as e:
        return redirect(url_for('index', tab='writing', message=f'Error: {e}', success='false'))

@app.route('/add-page', methods=['POST'])
def handle_add_page():
    try:
        add_to_home = request.form.get('add_to_home') == 'on'
        success, filename, added = add_page(
            title=request.form['title'],
            filename_or_slug=request.form.get('filename', ''),
            description=request.form.get('description', ''),
            abstract=request.form.get('abstract', ''),
            content_html=request.form['content'],
            add_to_home=add_to_home
        )
        if success:
            msg = f'Page created! File: pages/{filename}'
            if add_to_home and not added:
                msg += ' (Note: homepage insertion marker not found)'
            return redirect(url_for('index', tab='page', message=msg, success='true'))
        else:
            return redirect(url_for('index', tab='page', message='Error: could not create page', success='false'))
    except Exception as e:
        return redirect(url_for('index', tab='page', message=f'Error: {e}', success='false'))

@app.route('/deploy', methods=['POST'])
def handle_deploy():
    message = request.form.get('commit_message', 'Update wiki content')
    success, result = git_commit_and_push(message)
    return redirect(url_for('index', tab='deploy', message=result, success=str(success).lower()))

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  H. Aslan Wiki Manager")
    print("="*50)
    print(f"\n  Wiki location: {WIKI_ROOT}")
    print(f"\n  Open in browser: http://localhost:5000")
    print("\n  Press Ctrl+C to stop\n")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000)
