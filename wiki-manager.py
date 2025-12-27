#!/usr/bin/env python3
"""
H. Aslan Wiki Manager
A local web interface for adding content to your wiki.

SETUP:
    pip install flask markdown

USAGE:
    # Web interface
    python wiki-manager.py
    Then open http://localhost:5000 in your browser

    # Convert a single markdown file to HTML
    python wiki-manager.py convert path/to/file.md

    # Convert all markdown files in a directory
    python wiki-manager.py convert-all path/to/markdown/folder

    # Convert all and add to index
    python wiki-manager.py convert-all path/to/folder --index

The app writes directly to your HTML files. After adding content,
commit and push to deploy:
    git add . && git commit -m "Add new content" && git push
"""

import os
import re
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, redirect, url_for

# Try to import markdown library
try:
    import markdown
    from markdown.extensions.toc import TocExtension
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Warning: 'markdown' library not installed. Run: pip install markdown")

app = Flask(__name__)

# Get the directory where this script lives (your wiki root)
WIKI_ROOT = Path(__file__).parent.resolve()
PAGES_DIR = WIKI_ROOT / "pages"
WRITING_DIR = PAGES_DIR / "writing"
MARKDOWN_DIR = WIKI_ROOT / "markdown"  # Default location for markdown source files

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

def parse_date_string(date_str):
    """Parse various date formats into standardized formats"""
    date_str = date_str.strip()
    
    # Try various formats
    formats = [
        '%B %Y',        # December 2025
        '%b %Y',        # Dec 2025
        '%Y-%m-%d',     # 2025-12-15
        '%Y-%m',        # 2025-12
        '%d %B %Y',     # 15 December 2025
        '%d %b %Y',     # 15 Dec 2025
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return {
                'iso': dt.strftime('%Y-%m-%d') if '%d' in fmt else dt.strftime('%Y-%m'),
                'display': dt.strftime('%d %B %Y') if '%d' in fmt else dt.strftime('%B %Y'),
                'month_year': dt.strftime('%B %Y')
            }
        except ValueError:
            continue
    
    # Fallback to current date
    return get_current_date()

# Badge system mapping - categories to CSS classes and display names
BADGE_MAP = {
    'essay': {'class': 'badge-essay', 'label': 'Essay'},
    'sketch': {'class': 'badge-sketch', 'label': 'Sketch'},
    'notebook': {'class': 'badge-notebook', 'label': 'Notebook'},
    'fiction': {'class': 'badge-fiction', 'label': 'Fiction'},
    'verse': {'class': 'badge-verse', 'label': 'Verse'},
    'note': {'class': 'badge-note', 'label': 'Note'},
    'technical': {'class': 'badge-technical', 'label': 'Technical'},
    'draft': {'class': 'badge-draft', 'label': 'Draft'},
}

def get_badge_html(category):
    """Convert category to proper badge HTML"""
    cat_lower = category.lower().strip()
    
    if cat_lower in BADGE_MAP:
        badge = BADGE_MAP[cat_lower]
        return f'<span class="content-badge {badge["class"]}">{badge["label"]}</span>'
    
    # Fallback for unrecognized categories - use plain text
    return f'<span class="writing-category">{category}</span>'

def get_badge_data_category(category):
    """Get normalized data-category value"""
    return category.lower().strip()

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
# MARKDOWN CONVERSION
# ============================================

def parse_markdown_metadata(content):
    """
    Parse metadata from markdown content.
    
    Supports two formats:
    
    1. YAML frontmatter:
       ---
       title: My Title
       type: essay
       date: December 2025
       abstract: My abstract text
       tags: [tag1, tag2]
       ---
    
    2. Inline format (your current style):
       # My Title
       **ESSAY** · December 2025
       ---
       *ABSTRACT: My abstract text*
       ---
    """
    metadata = {
        'title': '',
        'type': 'essay',
        'date': get_current_date(),
        'abstract': '',
        'subtitle': '',
        'tags': [],
        'status': '',
        'epistemic': '',
    }
    
    lines = content.split('\n')
    body_start = 0
    
    # Check for YAML frontmatter
    if lines[0].strip() == '---':
        # Find closing ---
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                # Parse YAML-style frontmatter
                frontmatter = '\n'.join(lines[1:i])
                body_start = i + 1
                
                for fm_line in frontmatter.split('\n'):
                    if ':' in fm_line:
                        key, value = fm_line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip().strip('"\'')
                        
                        if key == 'title':
                            metadata['title'] = value
                        elif key == 'type' or key == 'category':
                            metadata['type'] = value.lower()
                        elif key == 'date' or key == 'created':
                            metadata['date'] = parse_date_string(value)
                        elif key == 'abstract' or key == 'description':
                            metadata['abstract'] = value
                        elif key == 'subtitle':
                            metadata['subtitle'] = value
                        elif key == 'tags':
                            # Handle both [tag1, tag2] and tag1, tag2 formats
                            value = value.strip('[]')
                            metadata['tags'] = [t.strip() for t in value.split(',') if t.strip()]
                        elif key == 'status':
                            metadata['status'] = value
                        elif key == 'epistemic':
                            metadata['epistemic'] = value
                break
    
    # Parse inline format (# Title, **TYPE** · Date, etc.)
    else:
        # Look for title (# heading)
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Title from # heading
            if line.startswith('# ') and not metadata['title']:
                metadata['title'] = line[2:].strip()
                body_start = max(body_start, i + 1)
            
            # Type and date from **TYPE** · Date
            type_date_match = re.match(r'\*\*(\w+)\*\*\s*[·•\-]\s*(.+)', line)
            if type_date_match:
                metadata['type'] = type_date_match.group(1).lower()
                metadata['date'] = parse_date_string(type_date_match.group(2))
                body_start = max(body_start, i + 1)
            
            # Abstract from *ABSTRACT: ...* (can span multiple lines until closing *)
            if line.startswith('*ABSTRACT:') or line.startswith('*Abstract:'):
                # Find the full abstract (may span multiple lines)
                abstract_text = line
                if not line.endswith('*') or line.count('*') < 2:
                    # Multi-line abstract
                    for j in range(i + 1, len(lines)):
                        abstract_text += ' ' + lines[j].strip()
                        if lines[j].strip().endswith('*'):
                            body_start = max(body_start, j + 1)
                            break
                else:
                    body_start = max(body_start, i + 1)
                
                # Extract text between *ABSTRACT: and closing *
                abstract_match = re.search(r'\*(?:ABSTRACT|Abstract):\s*(.+?)\*', abstract_text, re.DOTALL)
                if abstract_match:
                    metadata['abstract'] = abstract_match.group(1).strip()
            
            # Stop scanning after hitting main content (## heading or substantial text)
            if line.startswith('## ') and metadata['title']:
                break
            
            # Skip horizontal rules
            if line == '---':
                body_start = max(body_start, i + 1)
    
    # Get body content (everything after metadata)
    body_lines = lines[body_start:]
    
    # Clean up leading horizontal rules and empty lines from body
    while body_lines and (body_lines[0].strip() == '---' or body_lines[0].strip() == ''):
        body_lines.pop(0)
    
    body = '\n'.join(body_lines)
    
    return metadata, body


def convert_markdown_to_html(md_content):
    """
    Convert markdown content to HTML.
    
    Handles special elements:
    - <aside> tags preserved for sidenotes
    - ## headings get IDs for linking
    - Defined terms can be auto-linked
    """
    if not MARKDOWN_AVAILABLE:
        # Basic fallback conversion
        html = md_content
        # Convert headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        # Convert bold/italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        # Convert paragraphs
        html = re.sub(r'\n\n+', '</p>\n\n<p>', html)
        html = f'<p>{html}</p>'
        return html
    
    # Preserve <aside> tags by temporarily replacing them
    aside_placeholder = '___ASIDE_PLACEHOLDER_{}___'
    asides = []
    
    def save_aside(match):
        asides.append(match.group(0))
        return aside_placeholder.format(len(asides) - 1)
    
    # Save asides
    content = re.sub(r'<aside>.*?</aside>', save_aside, md_content, flags=re.DOTALL)
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=[
        'extra',           # Tables, fenced code, etc.
        'smarty',          # Smart quotes
        'sane_lists',      # Better list handling
        TocExtension(permalink=False, slugify=slugify),
    ])
    
    html = md.convert(content)
    
    # Restore asides
    for i, aside in enumerate(asides):
        # Convert markdown inside aside to HTML
        aside_inner = re.search(r'<aside>(.*?)</aside>', aside, re.DOTALL)
        if aside_inner:
            aside_content = aside_inner.group(1).strip()
            # Split aside into title (first line) and content
            aside_lines = aside_content.split('\n', 1)
            if len(aside_lines) == 2:
                aside_title = aside_lines[0].strip()
                aside_body = md.convert(aside_lines[1].strip())
                aside_html = f'''<aside class="sidenote">
    <span class="sidenote-title">{aside_title}</span>
    <div class="sidenote-content">{aside_body}</div>
</aside>'''
            else:
                aside_body = md.convert(aside_content)
                aside_html = f'<aside class="sidenote"><div class="sidenote-content">{aside_body}</div></aside>'
            
            html = html.replace(aside_placeholder.format(i), aside_html)
    
    # Add IDs to h2 and h3 tags for linking
    def add_heading_id(match):
        tag = match.group(1)
        content = match.group(2)
        heading_id = slugify(re.sub(r'<[^>]+>', '', content))  # Strip any HTML from content for ID
        return f'<{tag} id="{heading_id}">{content}</{tag}>'
    
    html = re.sub(r'<(h[23])>(.+?)</\1>', add_heading_id, html)
    
    return html


def convert_markdown_file(md_path, output_dir=None, add_to_index=True):
    """
    Convert a markdown file to HTML and optionally add to creative-writing index.
    
    Args:
        md_path: Path to the markdown file
        output_dir: Output directory (defaults to WRITING_DIR)
        add_to_index: Whether to add entry to creative-writing.html
    
    Returns:
        (success, output_path, metadata)
    """
    md_path = Path(md_path)
    output_dir = Path(output_dir) if output_dir else WRITING_DIR
    
    if not md_path.exists():
        return False, None, f"File not found: {md_path}"
    
    # Read markdown content
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse metadata and body
    metadata, body = parse_markdown_metadata(content)
    
    # Generate slug and filename
    slug = slugify(metadata['title'] or md_path.stem)
    filename = f"{slug}.html"
    output_path = output_dir / filename
    
    # Convert body to HTML
    body_html = convert_markdown_to_html(body)
    
    # Get badge HTML
    badge_html = get_badge_html(metadata['type'])
    data_category = get_badge_data_category(metadata['type'])
    dates = metadata['date']
    
    # Build abstract section if present
    abstract_html = ''
    if metadata['abstract']:
        abstract_html = f'''
            <div class="abstract">
                <p><span class="abstract-label">Abstract:</span> {metadata['abstract']}</p>
            </div>
'''
    
    # Build subtitle if present
    subtitle_html = ''
    if metadata['subtitle']:
        subtitle_html = f'<p class="page-subtitle">{metadata["subtitle"]}</p>'
    
    # Build epistemic status if present
    epistemic_html = ''
    if metadata['epistemic']:
        epistemic_html = f'''
            <div class="epistemic-status">
                <span class="epistemic-label">Epistemic status:</span> {metadata['epistemic']}
            </div>
'''
    
    # Create the full HTML page
    page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata['title']} · H. Aslan</title>
    <meta name="description" content="{metadata['abstract'][:160] if metadata['abstract'] else metadata['title']}">
    <meta name="type" content="{metadata['type']}">
    <meta name="date" content="{dates['iso']}">
    <link rel="stylesheet" href="../../assets/css/style.css">
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to content</a>
    
    <nav id="sidenav" class="sidenav">
        <div class="sidenav-header">
            <a href="../../index.html" class="site-title">H. Aslan</a>
            <span class="site-tagline">Not a tame lion.</span>
        </div>
        
        <div class="sidenav-section">
            <h2>Navigate</h2>
            <ul>
                <li><a href="../../index.html">Home</a></li>
                <li><a href="../about.html">About</a></li>
                <li><a href="../creative-writing.html">Writing</a></li>
                <li><a href="../definitions.html">Definitions</a></li>
            </ul>
        </div>
        
        <div class="sidenav-section">
            <h2>Topics</h2>
            <ul>
                <li><a href="../creative-writing.html#consciousness">Consciousness</a></li>
                <li><a href="../creative-writing.html#philosophy">Philosophy</a></li>
                <li><a href="../creative-writing.html#eastern">Eastern Traditions</a></li>
                <li><a href="../creative-writing.html#narrative">Narrative</a></li>
                <li><a href="../creative-writing.html#creative">Creative</a></li>
            </ul>
        </div>
        
        <div class="sidenav-footer">
            <p>&copy; 2024 H. Aslan</p>
        </div>
    </nav>

    <main id="main-content" class="main-content">
        <article class="entry">
            <a href="../creative-writing.html" class="back-link">← Back to Writing</a>
            
            <header class="entry-header">
                <h1>{metadata['title']}</h1>
                {subtitle_html}
                <div class="entry-meta">
                    {badge_html}
                    <time datetime="{dates['iso']}">{dates['display']}</time>
                </div>
            </header>
            
            {epistemic_html}
            {abstract_html}

            <div class="entry-content">
                {body_html}
            </div>
            
            <footer class="entry-footer">
                <p class="last-updated">Last updated: <time datetime="{dates['iso']}">{dates['month_year']}</time></p>
            </footer>
        </article>
    </main>

    <script src="../../assets/js/script.js"></script>
</body>
</html>
'''
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write the HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(page_html)
    
    print(f"  ✓ Converted: {md_path.name} → {filename}")
    
    # Add to creative-writing index if requested
    if add_to_index:
        success = add_to_writing_index(
            title=metadata['title'],
            filename=filename,
            category=metadata['type'],
            excerpt=metadata['abstract'],
            dates=dates
        )
        if success:
            print(f"    → Added to creative-writing.html index")
        else:
            print(f"    → Warning: Could not add to index (marker not found)")
    
    return True, output_path, metadata


def add_to_writing_index(title, filename, category, excerpt, dates):
    """Add an entry to the creative-writing.html index"""
    badge_html = get_badge_html(category)
    data_category = get_badge_data_category(category)
    
    # Truncate excerpt if too long
    if excerpt and len(excerpt) > 200:
        excerpt = excerpt[:197] + '...'
    
    index_entry = f'''
                    <div class="writing-card" data-category="{data_category}">
                        <h3><a href="writing/{filename}">{title}</a></h3>
                        <div class="writing-metadata">
                            {badge_html}
                            <time datetime="{dates['iso']}">{dates['display']}</time>
                        </div>
                        <p class="writing-excerpt">{excerpt or ""}</p>
                    </div>
'''
    
    index_file = PAGES_DIR / "creative-writing.html"
    
    if not index_file.exists():
        print(f"    Warning: {index_file} not found")
        return False
    
    with open(index_file, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    # Look for writing-grid marker
    marker = '<div class="writing-grid">'
    if marker in index_content:
        insert_pos = index_content.find(marker) + len(marker)
        new_content = index_content[:insert_pos] + index_entry + index_content[insert_pos:]
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    # Alternative: look for writing-list marker (topic-based index style)
    marker = '<ul class="writing-list">'
    if marker in index_content:
        insert_pos = index_content.find(marker) + len(marker)
        
        # Use list item format instead
        list_entry = f'''
                        <li class="writing-entry">
                            <a href="writing/{filename}" class="entry-link">
                                <span class="entry-title">{title}</span>
                                {badge_html}
                                <time class="entry-date" datetime="{dates['iso']}">{dates['month_year']}</time>
                            </a>
                            <p class="entry-description">{excerpt or ""}</p>
                        </li>
'''
        new_content = index_content[:insert_pos] + list_entry + index_content[insert_pos:]
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False


def convert_all_markdown(source_dir, output_dir=None, add_to_index=False):
    """
    Convert all markdown files in a directory to HTML.
    
    Args:
        source_dir: Directory containing markdown files
        output_dir: Output directory (defaults to WRITING_DIR)
        add_to_index: Whether to add entries to creative-writing.html
    """
    source_dir = Path(source_dir)
    output_dir = Path(output_dir) if output_dir else WRITING_DIR
    
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        return
    
    md_files = list(source_dir.glob('*.md'))
    
    if not md_files:
        print(f"No markdown files found in {source_dir}")
        return
    
    print(f"\nConverting {len(md_files)} markdown files...")
    print(f"  Source: {source_dir}")
    print(f"  Output: {output_dir}")
    print()
    
    success_count = 0
    for md_file in sorted(md_files):
        success, _, _ = convert_markdown_file(md_file, output_dir, add_to_index)
        if success:
            success_count += 1
    
    print(f"\nDone! Converted {success_count}/{len(md_files)} files.")


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
    
    # Get badge HTML for this category
    badge_html = get_badge_html(category)
    data_category = get_badge_data_category(category)
    
    # Create the writing page
    writing_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} · H. Aslan</title>
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
                    {badge_html}
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
                    <div class="writing-card" data-category="{data_category}">
                        <h3><a href="writing/{filename}">{title}</a></h3>
                        <div class="writing-metadata">
                            {badge_html}
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
  <title>{title} · H. Aslan</title>
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
            <nav class="flex space-x-8 overflow-x-auto">
                <a href="?tab=quote" class="py-3 px-1 text-sm font-medium whitespace-nowrap {{ 'tab-active' if tab == 'quote' else 'text-gray-500 hover:text-gray-700' }}">
                    Add Quote
                </a>
                <a href="?tab=definition" class="py-3 px-1 text-sm font-medium whitespace-nowrap {{ 'tab-active' if tab == 'definition' else 'text-gray-500 hover:text-gray-700' }}">
                    Add Definition
                </a>
                <a href="?tab=writing" class="py-3 px-1 text-sm font-medium whitespace-nowrap {{ 'tab-active' if tab == 'writing' else 'text-gray-500 hover:text-gray-700' }}">
                    Add Writing
                </a>
                <a href="?tab=convert" class="py-3 px-1 text-sm font-medium whitespace-nowrap {{ 'tab-active' if tab == 'convert' else 'text-gray-500 hover:text-gray-700' }}">
                    Convert MD
                </a>
                <a href="?tab=page" class="py-3 px-1 text-sm font-medium whitespace-nowrap {{ 'tab-active' if tab == 'page' else 'text-gray-500 hover:text-gray-700' }}">
                    Add Page
                </a>
                <a href="?tab=deploy" class="py-3 px-1 text-sm font-medium whitespace-nowrap {{ 'tab-active' if tab == 'deploy' else 'text-gray-500 hover:text-gray-700' }}">
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
                    placeholder="e.g., Epistemic Humility">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Definition (separate paragraphs with blank lines)</label>
                <textarea name="definition" rows="6" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="First paragraph of definition...

Second paragraph if needed..."></textarea>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Related Terms (optional, comma-separated)</label>
                <input type="text" name="related"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="e.g., Witness-Self, Consciousness|related, Ego|opposite">
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
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Title</label>
                <input type="text" name="title" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="e.g., The Witness and the Witnessed">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select name="category" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500">
                    <option value="essay">Essay</option>
                    <option value="sketch">Sketch</option>
                    <option value="notebook">Notebook</option>
                    <option value="fiction">Fiction</option>
                    <option value="verse">Verse</option>
                    <option value="note">Note</option>
                    <option value="technical">Technical</option>
                    <option value="draft">Draft</option>
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Excerpt (for index card)</label>
                <textarea name="excerpt" rows="2" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="A brief description for the index page..."></textarea>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Content (HTML)</label>
                <textarea name="content" rows="12" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500 font-mono text-sm"
                    placeholder="<p>Your content here...</p>"></textarea>
            </div>
            <button type="submit"
                class="w-full py-3 px-4 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-md transition">
                Create Writing
            </button>
        </form>
        {% endif %}

        <!-- Convert Markdown Form -->
        {% if tab == 'convert' %}
        <div class="space-y-6">
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 class="font-medium text-blue-800 mb-2">Markdown Conversion</h3>
                <p class="text-sm text-blue-700">
                    Convert markdown files to HTML. Files should have metadata in one of these formats:
                </p>
                <div class="mt-3 text-xs font-mono bg-white p-3 rounded border">
                    <div class="mb-2"><strong>Inline format:</strong></div>
                    <code># Title<br>**ESSAY** · December 2025<br>---<br>*ABSTRACT: Your abstract...*</code>
                </div>
            </div>
            
            <form method="POST" action="/convert-markdown" class="space-y-6">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Markdown File Path</label>
                    <input type="text" name="md_path" required
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500 font-mono text-sm"
                        placeholder="e.g., markdown/the-conductor-and-the-score.md">
                    <p class="mt-1 text-xs text-gray-500">Relative to wiki root: {{ wiki_root }}</p>
                </div>
                <div class="flex items-center gap-2">
                    <input type="checkbox" name="add_to_index" id="add_to_index" checked
                        class="h-4 w-4">
                    <label for="add_to_index" class="text-sm text-gray-700">Add to creative-writing.html index</label>
                </div>
                <button type="submit"
                    class="w-full py-3 px-4 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-md transition">
                    Convert File
                </button>
            </form>
            
            <div class="border-t pt-6">
                <h4 class="font-medium text-gray-700 mb-3">Or convert all files in a directory:</h4>
                <form method="POST" action="/convert-all-markdown" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Source Directory</label>
                        <input type="text" name="source_dir" required
                            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500 font-mono text-sm"
                            placeholder="e.g., markdown" value="markdown">
                    </div>
                    <div class="flex items-center gap-2">
                        <input type="checkbox" name="add_to_index_all" id="add_to_index_all"
                            class="h-4 w-4">
                        <label for="add_to_index_all" class="text-sm text-gray-700">Add all to index (careful with duplicates!)</label>
                    </div>
                    <button type="submit"
                        class="w-full py-3 px-4 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition">
                        Convert All in Directory
                    </button>
                </form>
            </div>
            
            <div class="bg-gray-100 p-4 rounded-lg">
                <h4 class="font-medium text-gray-700 mb-2">CLI Usage:</h4>
                <pre class="text-xs font-mono bg-gray-800 text-green-400 p-3 rounded overflow-x-auto">
# Convert single file
python wiki-manager.py convert path/to/file.md

# Convert all in directory
python wiki-manager.py convert-all markdown/

# Convert all and add to index
python wiki-manager.py convert-all markdown/ --index</pre>
            </div>
        </div>
        {% endif %}

        <!-- Page Form -->
        {% if tab == 'page' %}
        <form method="POST" action="/add-page" class="space-y-6">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Title</label>
                <input type="text" name="title" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-amber-500"
                    placeholder="e.g., Personal Domain">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Filename (optional)</label>
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

@app.route('/convert-markdown', methods=['POST'])
def handle_convert_markdown():
    try:
        md_path = WIKI_ROOT / request.form['md_path']
        add_to_index = request.form.get('add_to_index') == 'on'
        
        success, output_path, metadata = convert_markdown_file(md_path, add_to_index=add_to_index)
        
        if success:
            return redirect(url_for('index', tab='convert', 
                message=f'Converted! Output: {output_path.name}', success='true'))
        else:
            return redirect(url_for('index', tab='convert', 
                message=f'Error: {metadata}', success='false'))
    except Exception as e:
        return redirect(url_for('index', tab='convert', message=f'Error: {e}', success='false'))

@app.route('/convert-all-markdown', methods=['POST'])
def handle_convert_all_markdown():
    try:
        source_dir = WIKI_ROOT / request.form['source_dir']
        add_to_index = request.form.get('add_to_index_all') == 'on'
        
        convert_all_markdown(source_dir, add_to_index=add_to_index)
        
        return redirect(url_for('index', tab='convert', 
            message=f'Batch conversion complete! Check console for details.', success='true'))
    except Exception as e:
        return redirect(url_for('index', tab='convert', message=f'Error: {e}', success='false'))

@app.route('/deploy', methods=['POST'])
def handle_deploy():
    message = request.form.get('commit_message', 'Update wiki content')
    success, result = git_commit_and_push(message)
    return redirect(url_for('index', tab='deploy', message=result, success=str(success).lower()))

# ============================================
# CLI
# ============================================

def cli():
    """Command-line interface for wiki-manager"""
    parser = argparse.ArgumentParser(
        description='H. Aslan Wiki Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python wiki-manager.py                     # Start web interface
  python wiki-manager.py convert file.md    # Convert single file
  python wiki-manager.py convert-all md/    # Convert all in directory
  python wiki-manager.py convert-all md/ --index  # Convert and add to index
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command')
    
    # Convert single file
    convert_parser = subparsers.add_parser('convert', help='Convert a markdown file to HTML')
    convert_parser.add_argument('file', help='Path to markdown file')
    convert_parser.add_argument('--output', '-o', help='Output directory (default: pages/writing)')
    convert_parser.add_argument('--no-index', action='store_true', help='Do not add to creative-writing index')
    
    # Convert all files
    convert_all_parser = subparsers.add_parser('convert-all', help='Convert all markdown files in directory')
    convert_all_parser.add_argument('directory', help='Source directory containing markdown files')
    convert_all_parser.add_argument('--output', '-o', help='Output directory (default: pages/writing)')
    convert_all_parser.add_argument('--index', action='store_true', help='Add entries to creative-writing index')
    
    args = parser.parse_args()
    
    if args.command == 'convert':
        if not MARKDOWN_AVAILABLE:
            print("Error: 'markdown' library required. Run: pip install markdown")
            sys.exit(1)
        
        success, output_path, metadata = convert_markdown_file(
            args.file,
            output_dir=args.output,
            add_to_index=not args.no_index
        )
        sys.exit(0 if success else 1)
        
    elif args.command == 'convert-all':
        if not MARKDOWN_AVAILABLE:
            print("Error: 'markdown' library required. Run: pip install markdown")
            sys.exit(1)
        
        convert_all_markdown(
            args.directory,
            output_dir=args.output,
            add_to_index=args.index
        )
        
    else:
        # No command specified - start web server
        print("\n" + "="*50)
        print("  H. Aslan Wiki Manager")
        print("="*50)
        print(f"\n  Wiki location: {WIKI_ROOT}")
        print(f"\n  Open in browser: http://localhost:5000")
        print("\n  Press Ctrl+C to stop\n")
        print("="*50 + "\n")
        
        app.run(debug=True, port=5000)

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    cli()
