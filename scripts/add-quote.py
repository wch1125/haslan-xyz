"""
Add Quote Script for H. Aslan Wiki
Automates the process of adding new quotes to quotes.html
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

def create_quote_html(quote_text, author, source, year, tags):
    """Generate HTML for a new quote entry"""
    date_added = datetime.now().strftime("%Y-%m-%d")
    
    # Format tags
    tags_str = ','.join(tags)
    tags_html = ''.join([f'<span class="quote-tag">{tag}</span>' for tag in tags])
    
    # Create source info
    source_info = f"{source}"
    if year:
        source_info += f" ({year})"
    
    html = f'''
                <div class="quote-entry" data-tags="{tags_str}" data-date="{date_added}">
                    <blockquote class="quote-text">
                        {quote_text}
                    </blockquote>
                    <div class="quote-attribution">
                        <span class="quote-author">{author}</span>
                        <span class="quote-source">{source_info}</span>
                    </div>
                    <div class="quote-metadata">
                        <div class="quote-tags">
                            {tags_html}
                        </div>
                        <time class="quote-date" datetime="{date_added}">Added {datetime.now().strftime("%B %Y")}</time>
                    </div>
                </div>
'''
    return html

def insert_quote(quotes_file, new_html):
    """Insert new quote at the top of the quotes list"""
    with open(quotes_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the quotes-list section
    list_pattern = r'(<section id="quotes-list">.*?<h2>Quotes</h2>)(.*?)(</section>)'
    match = re.search(list_pattern, content, re.DOTALL)
    
    if not match:
        print("Error: Could not find quotes list section")
        return False
    
    before = match.group(1)
    quotes = match.group(2)
    after = match.group(3)
    
    # Insert new quote at the beginning (most recent first)
    updated_quotes = new_html + quotes
    
    # Reconstruct content
    new_content = content[:match.start()] + before + updated_quotes + after + content[match.end():]
    
    # Write updated content
    with open(quotes_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    print("=" * 50)
    print("H. Aslan Wiki - Add Quote")
    print("=" * 50)
    print()
    
    # Get script directory
    script_dir = Path(__file__).parent
    wiki_root = script_dir.parent
    quotes_file = wiki_root / "pages" / "quotes.html"
    
    if not quotes_file.exists():
        print(f"Error: Could not find quotes.html at {quotes_file}")
        sys.exit(1)
    
    # Collect information
    print("Enter quote text (can be multiple lines, empty line to finish):")
    quote_lines = []
    while True:
        line = input()
        if not line:
            break
        quote_lines.append(line)
    
    if not quote_lines:
        print("Error: Quote text cannot be empty")
        sys.exit(1)
    
    quote_text = ' '.join(quote_lines)
    
    author = get_input("\nAuthor: ")
    source = get_input("Source (book, article, speech, etc.): ")
    year = get_input("Year (or press Enter to skip): ", required=False)
    
    print("\nTags (comma-separated, e.g., 'philosophy,creativity,identity'):")
    tags_input = get_input("Tags: ")
    tags = [tag.strip().lower() for tag in tags_input.split(',')]
    
    # Generate HTML
    html = create_quote_html(quote_text, author, source, year, tags)
    
    # Preview
    print("\n" + "=" * 50)
    print("Preview:")
    print("=" * 50)
    print(html)
    print("=" * 50)
    
    # Confirm
    confirm = get_input("\nAdd this quote? (y/n): ").lower()
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Insert into file
    if insert_quote(quotes_file, html):
        print(f"\n✓ Quote added successfully!")
        print(f"  Author: {author}")
        print(f"  Source: {source}")
        print(f"  Tags: {', '.join(tags)}")
        print(f"  File: {quotes_file}")
        print()
        print("Note: If you used new tags, update the filter buttons in quotes.html")
    else:
        print("\n✗ Error adding quote")
        sys.exit(1)

if __name__ == '__main__':
    main()
