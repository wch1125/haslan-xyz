"""
Add Definition Script for H. Aslan Wiki
Automates the process of adding new definitions to definitions.html
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
    """Convert term to URL-friendly slug"""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug

def get_first_letter(term):
    """Get first letter for alphabetical organization"""
    return term[0].upper()

def create_definition_html(term, definition, related_terms=None):
    """Generate HTML for a new definition entry"""
    slug = slugify(term)
    letter = get_first_letter(term)
    date = datetime.now().strftime("%B %Y")
    
    html = f'''
                <div class="definition-entry" id="{slug}">
                    <h3><span class="definition-term">{term}</span></h3>
                    <div class="definition-metadata">
                        <span class="definition-letter">{letter}</span>
                        <span class="definition-date">Added: {date}</span>
                    </div>
                    <div class="definition-content">
                        {definition}
'''
    
    if related_terms:
        html += '''
                        <details class="collapse">
                            <summary>Related Concepts</summary>
                            <div class="collapse-content">
                                <ul>
'''
        for related in related_terms:
            related_slug = slugify(related)
            html += f'                                    <li><a href="#{related_slug}">{related}</a></li>\n'
        
        html += '''                                </ul>
                            </div>
                        </details>
'''
    
    html += '''                    </div>
                </div>
'''
    return html

def insert_definition(definitions_file, new_html, term):
    """Insert new definition in alphabetical order"""
    with open(definitions_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the definitions-list section
    list_pattern = r'(<section id="definitions-list">.*?<h2>Definitions</h2>)(.*?)(<!-- Template for new definitions|</section>)'
    match = re.search(list_pattern, content, re.DOTALL)
    
    if not match:
        print("Error: Could not find definitions list section")
        return False
    
    before = match.group(1)
    definitions = match.group(2)
    after = match.group(3)
    
    # Insert new definition (simple append for now, alphabetical sorting can be added)
    updated_definitions = definitions + new_html
    
    # Reconstruct content
    new_content = content[:match.start()] + before + updated_definitions + after + content[match.end():]
    
    # Update alphabetical index if needed
    letter = get_first_letter(term)
    index_pattern = r'<div class="definition-index">(.*?)</div>'
    index_match = re.search(index_pattern, new_content, re.DOTALL)
    
    if index_match:
        index_content = index_match.group(1)
        letter_link = f'<a href="#{letter}">{letter}</a>'
        if letter_link not in index_content:
            # Add new letter to index
            print(f"Note: Add '{letter_link}' to the alphabetical index manually")
    
    # Write updated content
    with open(definitions_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    print("=" * 50)
    print("H. Aslan Wiki - Add Definition")
    print("=" * 50)
    print()
    
    # Get script directory
    script_dir = Path(__file__).parent
    wiki_root = script_dir.parent
    definitions_file = wiki_root / "pages" / "definitions.html"
    
    if not definitions_file.exists():
        print(f"Error: Could not find definitions.html at {definitions_file}")
        sys.exit(1)
    
    # Collect information
    term = get_input("Term name (e.g., 'Empathy'): ")
    print(f"\nSlug will be: {slugify(term)}")
    print(f"Letter: {get_first_letter(term)}")
    print()
    
    print("Enter definition paragraphs (enter empty line when done):")
    print("Tip: Use <p> tags for paragraphs, <em> for emphasis, <strong> for bold")
    print()
    
    definition_lines = []
    while True:
        line = input()
        if not line:
            break
        definition_lines.append(line)
    
    if not definition_lines:
        print("Error: Definition cannot be empty")
        sys.exit(1)
    
    # Ensure paragraphs are wrapped in <p> tags
    definition_paragraphs = []
    for line in definition_lines:
        line = line.strip()
        if not line.startswith('<p>'):
            line = f'<p>{line}</p>'
        definition_paragraphs.append(' ' * 24 + line)
    
    definition = '\n'.join(definition_paragraphs)
    
    # Related terms (optional)
    print("\nRelated terms (comma-separated, or press Enter to skip):")
    related_input = input().strip()
    related_terms = [t.strip() for t in related_input.split(',')] if related_input else None
    
    # Generate HTML
    html = create_definition_html(term, definition, related_terms)
    
    # Preview
    print("\n" + "=" * 50)
    print("Preview:")
    print("=" * 50)
    print(html)
    print("=" * 50)
    
    # Confirm
    confirm = get_input("\nAdd this definition? (y/n): ").lower()
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Insert into file
    if insert_definition(definitions_file, html, term):
        print(f"\n✓ Definition added successfully!")
        print(f"  Term: {term}")
        print(f"  Slug: {slugify(term)}")
        print(f"  File: {definitions_file}")
        print()
        print("Next steps:")
        print(f"1. Review the entry in definitions.html")
        print(f"2. Update the alphabetical index if needed")
        print(f"3. Reference the term in other pages using:")
        print(f'   <a href="pages/definitions.html#{slugify(term)}" class="definition-link"')
        print(f'      data-term="{term}"')
        print(f'      data-definition="Brief popup text">{term}</a>')
    else:
        print("\n✗ Error adding definition")
        sys.exit(1)

if __name__ == '__main__':
    main()
