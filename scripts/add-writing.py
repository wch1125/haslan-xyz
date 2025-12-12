"""
Add Writing Script for H. Aslan Wiki
Automates the process of adding new creative writing pieces
"""

import sys
import re
from datetime import datetime
from pathlib import Path

def get_input(prompt, required=True):
    """Get user input with optional requirement"""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("This field is required. Please enter a value.")

def slugify(text):
    """Convert title to URL-friendly slug"""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug

def create_writing_page(title, slug, content, category, date):
    """Generate HTML for a new writing piece"""
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} • H. Aslan</title>
    <meta name="description" content="{title} - Creative writing by H. Aslan">
    <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
    <nav id="sidenav">
        <div class="nav-header">
            <h1><a href="../index.html">H. Aslan</a></h1>
            <p class="tagline">Observations & Analysis</p>
        </div>
        
        <section class="nav-section">
            <h2>Topics</h2>
            <ul>
                <li><a href="creative-writing.html">Creative Writing</a></li>
                <li><a href="quotes.html">Quotes</a></li>
                <li><a href="definitions.html">Definitions</a></li>
            </ul>
        </section>

        <section class="nav-section">
            <h2>Projects</h2>
            <ul>
                <li><a href="credit-agreement.html">The HTML Credit Agreement</a></li>
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
            <a href="creative-writing.html" class="back-link">Back to Creative Writing</a>
            
            <header class="page-header">
                <h1>{title}</h1>
                <div class="page-metadata">
                    <span class="writing-category">{category}</span>
                    <time datetime="{date}">{datetime.strptime(date, "%Y-%m-%d").strftime("%d %B %Y")}</time>
                </div>
            </header>

            <section class="writing-content">
{content}
            </section>
        </article>
    </main>

    <script src="../assets/js/script.js"></script>
</body>
</html>
'''
    return html

def create_index_entry(title, slug, excerpt, category, date):
    """Generate HTML for index entry on creative-writing.html"""
    formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d %B %Y")
    
    html = f'''
                    <div class="writing-card" data-category="{category.lower()}">
                        <h3><a href="writing/{slug}.html">{title}</a></h3>
                        <div class="writing-metadata">
                            <span class="writing-category">{category}</span>
                            <time datetime="{date}">{formatted_date}</time>
                        </div>
                        <p class="writing-excerpt">{excerpt}</p>
                    </div>
'''
    return html

def insert_index_entry(index_file, new_html):
    """Insert new entry into creative-writing.html index"""
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the writing-grid section
    grid_pattern = r'(<div class="writing-grid">)(.*?)(</div>)'
    match = re.search(grid_pattern, content, re.DOTALL)
    
    if not match:
        print("Error: Could not find writing-grid section")
        return False
    
    before = match.group(1)
    entries = match.group(2)
    after = match.group(3)
    
    # Insert new entry at the beginning (most recent first)
    updated_entries = new_html + entries
    
    # Reconstruct content
    new_content = content[:match.start()] + before + updated_entries + after + content[match.end():]
    
    # Write updated content
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    print("=" * 50)
    print("H. Aslan Wiki - Add Creative Writing")
    print("=" * 50)
    print()
    
    # Get script directory
    script_dir = Path(__file__).parent
    wiki_root = script_dir.parent
    writing_dir = wiki_root / "pages" / "writing"
    index_file = wiki_root / "pages" / "creative-writing.html"
    
    # Create writing directory if it doesn't exist
    writing_dir.mkdir(parents=True, exist_ok=True)
    
    if not index_file.exists():
        print(f"Error: Could not find creative-writing.html at {index_file}")
        sys.exit(1)
    
    # Collect information
    title = get_input("Title: ")
    slug = slugify(title)
    print(f"Slug will be: {slug}")
    print()
    
    print("Category options: Short Story, Poem, Essay, Fragment, Dialogue")
    category = get_input("Category: ")
    
    date = datetime.now().strftime("%Y-%m-%d")
    print(f"Date: {date}")
    print()
    
    excerpt = get_input("Brief excerpt (1-2 sentences for the index): ")
    print()
    
    print("Enter content (type 'END' on a new line when finished):")
    print("Tip: Use <p> tags for paragraphs, <em> for emphasis")
    print()
    
    content_lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        content_lines.append(line)
    
    if not content_lines:
        print("Error: Content cannot be empty")
        sys.exit(1)
    
    # Format content with proper indentation
    formatted_content = []
    for line in content_lines:
        if line.strip():
            formatted_content.append(' ' * 16 + line)
        else:
            formatted_content.append('')
    
    content = '\n'.join(formatted_content)
    
    # Generate HTMLs
    page_html = create_writing_page(title, slug, content, category, date)
    index_html = create_index_entry(title, slug, excerpt, category, date)
    
    # Preview
    print("\n" + "=" * 50)
    print("Preview - Page:")
    print("=" * 50)
    print(page_html[:500] + "...")
    print("\n" + "=" * 50)
    print("Preview - Index Entry:")
    print("=" * 50)
    print(index_html)
    print("=" * 50)
    
    # Confirm
    confirm = get_input("\nAdd this writing piece? (y/n): ").lower()
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Create the page file
    page_file = writing_dir / f"{slug}.html"
    with open(page_file, 'w', encoding='utf-8') as f:
        f.write(page_html)
    
    # Insert into index
    if insert_index_entry(index_file, index_html):
        print(f"\n✓ Writing piece added successfully!")
        print(f"  Title: {title}")
        print(f"  Slug: {slug}")
        print(f"  Page: {page_file}")
        print(f"  Index: {index_file}")
        print()
        print("Next steps:")
        print("1. Review the page and index entry")
        print("2. Add any definition links as needed")
        print("3. Commit and push to GitHub")
    else:
        print("\n✗ Error updating index")
        sys.exit(1)

if __name__ == '__main__':
    main()
