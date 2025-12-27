#!/usr/bin/env python3
"""
H. Aslan Wiki - Complete Build System
======================================

Converts markdown essays to HTML AND auto-generates:
- Topic-based index page (creative-writing.html) - like Gwern's index
- Definition entries for new terms

Usage:
    python build_wiki.py essay.md              # Build single essay + update index
    python build_wiki.py rebuild-index         # Rebuild index from all essays
    python build_wiki.py list-topics           # Show all topics
    python build_wiki.py add-definition "Term" "Definition text"

Front Matter Format:
---
title: The Title of the Essay
date: 2025-12-25
type: sketch                  # essay, sketch, notebook, fiction, draft
topic: consciousness          # For grouping in index (see TOPIC_ORDER below)
abstract: A brief description...
claims_not_making:
  - First disclaimer
update_triggers:
  - What would change my mind
definitions:                  # Auto-add these to definitions.html
  - term: Conductor
    definition: The witness-self as interpretive presence
  - term: Audience  
    definition: Brahman understood as universal witness
---

What is an HTML "flourish"?
  Custom formatting beyond the template: special callout boxes, unique 
  section styling, embedded diagrams, custom CSS for a specific piece.
  Things the automated converter can't anticipate.
"""

import argparse
import re
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

try:
    import yaml
    import markdown
except ImportError:
    print("Required packages not found. Install with:")
    print("  pip install pyyaml markdown --break-system-packages")
    sys.exit(1)


# =============================================================================
# CONFIGURATION - Edit these for your site
# =============================================================================

WIKI_ROOT = Path(".")
ESSAYS_DIR = WIKI_ROOT / "pages" / "writing"
PAGES_DIR = WIKI_ROOT / "pages"
INDEX_FILE = PAGES_DIR / "creative-writing.html"
DEFINITIONS_FILE = PAGES_DIR / "definitions.html"
ESSAYS_JSON = WIKI_ROOT / ".essays-metadata.json"  # Cache for rebuilds

# Topic order and display names - essays grouped by these categories
# Add new topics here as your wiki grows
TOPIC_ORDER = [
    ("consciousness", "Consciousness & The Symphony"),
    ("ethics", "Ethics & Moral Philosophy"),
    ("institutions", "Institutions & Power"),
    ("technology", "Technology & AI"),
    ("speculation", "Speculation & Fiction"),
    ("awareness", "Awareness & Meta-Cognition"),
    ("personal", "Personal & Meta"),
    ("uncategorized", "Other"),
]

TOPIC_MAP = {k: v for k, v in TOPIC_ORDER}

BADGE_MAP = {
    'essay': ('essay', 'Essay'),
    'sketch': ('sketch', 'Sketch'),
    'notebook': ('notebook', 'Notebook'),
    'fiction': ('fiction', 'Fiction'),
    'draft': ('draft', 'Draft'),
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class Essay:
    """Represents an essay's metadata."""
    filename: str
    title: str
    date: datetime
    type: str
    topic: str
    abstract: str
    claims_not_making: list = field(default_factory=list)
    update_triggers: list = field(default_factory=list)
    definitions: list = field(default_factory=list)
    
    def to_dict(self):
        return {
            "filename": self.filename,
            "title": self.title,
            "date": self.date.isoformat(),
            "type": self.type,
            "topic": self.topic,
            "abstract": self.abstract,
            "claims_not_making": self.claims_not_making,
            "update_triggers": self.update_triggers,
            "definitions": self.definitions,
        }
    
    @classmethod
    def from_dict(cls, d):
        d = d.copy()
        d["date"] = datetime.fromisoformat(d["date"])
        return cls(**d)


# =============================================================================
# MARKDOWN PROCESSING
# =============================================================================

def parse_front_matter(content: str) -> tuple[dict, str]:
    """Extract YAML front matter and return (metadata, body)."""
    if not content.startswith('---'):
        return {}, content
    
    end_match = re.search(r'\n---\s*\n', content[3:])
    if not end_match:
        return {}, content
    
    yaml_content = content[3:end_match.start() + 3]
    body = content[end_match.end() + 3:]
    
    try:
        metadata = yaml.safe_load(yaml_content) or {}
    except yaml.YAMLError as e:
        print(f"Warning: Could not parse YAML front matter: {e}")
        metadata = {}
    
    return metadata, body.strip()


def process_definition_links(text: str) -> str:
    """Convert [[term]] and [[term|display]] to definition links."""
    def replace_def_link(match):
        full_match = match.group(1)
        if '|' in full_match:
            term, display = full_match.split('|', 1)
        else:
            term = display = full_match
        anchor = term.lower().strip().replace(' ', '-')
        return (f'<a href="../definitions.html#{anchor}" class="definition-link" '
                f'data-term="{term.strip()}">{display.strip()}</a>')
    return re.sub(r'\[\[([^\]]+)\]\]', replace_def_link, text)


def process_sections(html: str) -> str:
    """Wrap h2 sections in <section> tags with IDs."""
    lines = html.split('\n')
    result = []
    in_section = False
    
    for line in lines:
        h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', line)
        if h2_match:
            if in_section:
                result.append('</section>')
            h2_text = re.sub(r'<[^>]+>', '', h2_match.group(1))  # Strip inner tags
            section_id = re.sub(r'[^\w\s-]', '', h2_text.lower())
            section_id = re.sub(r'\s+', '-', section_id.strip())
            result.append(f'<section id="{section_id}">')
            in_section = True
        result.append(line)
    
    if in_section:
        result.append('</section>')
    return '\n'.join(result)


def markdown_to_html(md_content: str) -> str:
    """Convert markdown to HTML with custom processing."""
    md_content = process_definition_links(md_content)
    md = markdown.Markdown(extensions=['fenced_code', 'tables', 'toc', 'smarty'])
    html = md.convert(md_content)
    return process_sections(html)


# =============================================================================
# HTML TEMPLATES
# =============================================================================

ESSAY_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} • H. Aslan</title>
    <meta name="description" content="{meta_description}">
    <link rel="stylesheet" href="../../assets/css/style.css">
</head>
<body>
    <nav id="sidenav">
        <div class="nav-header">
            <h1><a href="../../index.html">H. Aslan</a></h1>
            <p class="tagline">Not a tame lion.</p>
        </div>
        <section class="nav-section">
            <h2>Explore</h2>
            <ul>
                <li><a href="../creative-writing.html">Writing</a></li>
                <li><a href="../quotes.html">Quotes</a></li>
                <li><a href="../definitions.html">Definitions</a></li>
            </ul>
        </section>
        <section class="nav-section">
            <h2>Meta</h2>
            <ul>
                <li><a href="../how-to-read-this-site.html">How to Read This</a></li>
                <li><a href="../personal-domain.html">Why This Exists</a></li>
                <li><a href="../colophon.html">Colophon</a></li>
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
            <a href="../creative-writing.html" class="back-link">← Back to Writing</a>
            <header class="page-header">
                <h1>{title}</h1>
                <div class="page-metadata">
                    <span class="content-badge badge-{badge_class}">{badge_label}</span>
                    <time datetime="{date_iso}">{date_display}</time>
                </div>
            </header>

            <section class="writing-content">
                {abstract_section}
                {disclaimers_section}
                {content}
            </section>
        </article>
    </main>
    <script src="../../assets/js/script.js"></script>
</body>
</html>'''


INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Writing • H. Aslan</title>
    <meta name="description" content="Essays, sketches, and creative work organized by topic">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='45' fill='%23B8860B'/%3E%3Ccircle cx='35' cy='42' r='6' fill='%23fff'/%3E%3Ccircle cx='65' cy='42' r='6' fill='%23fff'/%3E%3Cellipse cx='50' cy='62' rx='12' ry='8' fill='%23fff'/%3E%3C/svg%3E">
    <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
    <a href="#content" class="skip-link">Skip to content</a>

    <div class="loading-screen" id="loading-screen">
        <div class="loading-motes">
            <div class="loading-mote"></div>
            <div class="loading-mote"></div>
            <div class="loading-mote"></div>
            <div class="loading-mote"></div>
            <div class="loading-mote"></div>
        </div>
        <div class="loading-brand">
            <div class="loading-brand-name">H. Aslan</div>
            <div class="loading-brand-sub">Not a tame lion.</div>
        </div>
        <div class="loading-bar">
            <div class="loading-bar-fill"></div>
        </div>
        <button class="loading-skip">Skip</button>
    </div>

    <nav id="sidenav" aria-label="Main navigation">
        <div class="nav-header">
            <h1><a href="../index.html">H. Aslan</a></h1>
            <p class="tagline">Not a tame lion.</p>
        </div>
        <section class="nav-section">
            <h2>Explore</h2>
            <ul>
                <li><a href="creative-writing.html">Writing</a></li>
                <li><a href="quotes.html">Quotes</a></li>
                <li><a href="definitions.html">Definitions</a></li>
            </ul>
        </section>
        <section class="nav-section">
            <h2>Meta</h2>
            <ul>
                <li><a href="how-to-read-this-site.html">How to Read This</a></li>
                <li><a href="personal-domain.html">Why This Exists</a></li>
                <li><a href="colophon.html">Colophon</a></li>
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
            <a href="../index.html" class="back-link">← Home</a>
            
            <header class="page-header">
                <h1>Writing</h1>
            </header>
            
            <div class="abstract">
                <p><span class="abstract-label">Abstract:</span> Essays, sketches, and speculative work organized by topic. Badges indicate status: <span class="content-badge badge-essay">Essay</span> for argued pieces, <span class="content-badge badge-sketch">Sketch</span> for explorations, <span class="content-badge badge-fiction">Fiction</span> for creative work, <span class="content-badge badge-draft">Draft</span> for works in progress.</p>
            </div>

            <!-- TABLE OF CONTENTS -->
            <nav class="toc" aria-label="Table of contents">
                <h2>Topics</h2>
                <ul class="toc-list">
{toc_entries}
                </ul>
            </nav>

            <hr class="section-divider">

            <!-- TOPIC SECTIONS -->
{topic_sections}

            <div class="paw-divider">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="8" r="3"/>
                    <circle cx="6" cy="6" r="2"/>
                    <circle cx="18" cy="6" r="2"/>
                    <circle cx="4" cy="11" r="2"/>
                    <circle cx="20" cy="11" r="2"/>
                    <ellipse cx="12" cy="15" rx="5" ry="4"/>
                </svg>
            </div>

            <footer class="page-footer">
                <p class="smallcaps">Index auto-generated · {essay_count} essays · Last updated {generation_date}</p>
            </footer>
        </article>
    </main>
    <script src="../assets/js/script.js"></script>
</body>
</html>'''


# =============================================================================
# CACHE FUNCTIONS
# =============================================================================

def load_essays_cache() -> dict[str, Essay]:
    """Load cached essay metadata."""
    if ESSAYS_JSON.exists():
        try:
            with open(ESSAYS_JSON, 'r') as f:
                data = json.load(f)
                return {k: Essay.from_dict(v) for k, v in data.items()}
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load cache: {e}")
    return {}


def save_essays_cache(essays: dict[str, Essay]):
    """Save essay metadata cache."""
    data = {k: v.to_dict() for k, v in essays.items()}
    with open(ESSAYS_JSON, 'w') as f:
        json.dump(data, f, indent=2, default=str)


# =============================================================================
# CORE BUILD FUNCTIONS
# =============================================================================

def parse_essay_file(md_path: Path) -> tuple[dict, str, Essay]:
    """Parse a markdown file and return (metadata, body, Essay object)."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    metadata, body = parse_front_matter(content)
    
    # Parse date
    date_str = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
    if isinstance(date_str, datetime):
        date_obj = date_str
    else:
        try:
            date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
        except ValueError:
            date_obj = datetime.now()
    
    # Generate filename from title
    title = metadata.get('title', 'Untitled')
    filename = re.sub(r'[^\w\s-]', '', title.lower())
    filename = re.sub(r'\s+', '-', filename.strip()) + '.html'
    
    essay = Essay(
        filename=filename,
        title=title,
        date=date_obj,
        type=metadata.get('type', 'sketch').lower(),
        topic=metadata.get('topic', 'uncategorized').lower(),
        abstract=metadata.get('abstract', ''),
        claims_not_making=metadata.get('claims_not_making', []),
        update_triggers=metadata.get('update_triggers', []),
        definitions=metadata.get('definitions', []),
    )
    
    return metadata, body, essay


def build_essay_html(md_path: Path, output_path: Optional[Path] = None) -> tuple[str, Path, Essay]:
    """Build HTML from markdown. Returns (html, output_path, essay)."""
    metadata, body, essay = parse_essay_file(md_path)
    
    if output_path is None:
        output_path = ESSAYS_DIR / essay.filename
    
    badge_class, badge_label = BADGE_MAP.get(essay.type, ('sketch', 'Sketch'))
    
    # Abstract section
    abstract_section = ''
    if essay.abstract:
        abstract_processed = process_definition_links(essay.abstract)
        abstract_section = f'''<div class="abstract">
    <p><span class="abstract-label">Abstract:</span> {abstract_processed}</p>
</div>'''
    
    # Disclaimers section
    disclaimers_section = ''
    if essay.claims_not_making or essay.update_triggers:
        claims = '\n'.join(f'            <li>{c}</li>' for c in essay.claims_not_making)
        triggers = '\n'.join(f'            <li>{t}</li>' for t in essay.update_triggers)
        disclaimers_section = f'''<details class="collapse">
    <summary>What this {essay.type} is and is not claiming</summary>
    <div class="collapse-content">
        <p><strong>What this {essay.type} is NOT claiming:</strong></p>
        <ul>
{claims}
        </ul>
        <p><strong>What would change my mind / update this model:</strong></p>
        <ul>
{triggers}
        </ul>
    </div>
</details>'''
    
    body_html = markdown_to_html(body)
    meta_desc = (essay.abstract[:157] + '...') if len(essay.abstract) > 160 else essay.abstract
    
    html = ESSAY_TEMPLATE.format(
        title=essay.title,
        meta_description=meta_desc.replace('"', '&quot;'),
        badge_class=badge_class,
        badge_label=badge_label,
        date_iso=essay.date.strftime('%Y-%m'),
        date_display=essay.date.strftime('%B %Y'),
        abstract_section=abstract_section,
        disclaimers_section=disclaimers_section,
        content=body_html,
    )
    
    return html, output_path, essay


def generate_index_page(essays: dict[str, Essay]) -> str:
    """Generate the topic-based index page (Gwern-style)."""
    # Group by topic
    by_topic = {}
    for essay in essays.values():
        topic = essay.topic if essay.topic in TOPIC_MAP else 'uncategorized'
        by_topic.setdefault(topic, []).append(essay)
    
    # Sort within topics by date (newest first)
    for topic in by_topic:
        by_topic[topic].sort(key=lambda e: e.date, reverse=True)
    
    # Generate TOC
    toc_lines = []
    for topic_id, topic_name in TOPIC_ORDER:
        if topic_id in by_topic and by_topic[topic_id]:
            count = len(by_topic[topic_id])
            toc_lines.append(
                f'                    <li><a href="#{topic_id}">{topic_name}</a> <span class="toc-count">({count})</span></li>'
            )
    
    # Generate topic sections
    sections = []
    for topic_id, topic_name in TOPIC_ORDER:
        if topic_id not in by_topic or not by_topic[topic_id]:
            continue
        
        entries = []
        for essay in by_topic[topic_id]:
            badge_class, badge_label = BADGE_MAP.get(essay.type, ('sketch', 'Sketch'))
            abstract_short = (essay.abstract[:180] + '...') if len(essay.abstract) > 180 else essay.abstract
            
            entries.append(f'''                    <div class="writing-entry" data-type="{essay.type}">
                        <div class="entry-header">
                            <h3><a href="writing/{essay.filename}">{essay.title}</a></h3>
                            <div class="entry-meta">
                                <span class="content-badge badge-{badge_class}">{badge_label}</span>
                                <time datetime="{essay.date.strftime('%Y-%m')}">{essay.date.strftime('%b %Y')}</time>
                            </div>
                        </div>
                        <p class="entry-abstract">{abstract_short}</p>
                    </div>''')
        
        sections.append(f'''
            <section id="{topic_id}" class="topic-section">
                <h2>{topic_name}</h2>
                <div class="writing-list">
{chr(10).join(entries)}
                </div>
            </section>''')
    
    return INDEX_TEMPLATE.format(
        toc_entries='\n'.join(toc_lines),
        topic_sections='\n'.join(sections),
        essay_count=len(essays),
        generation_date=datetime.now().strftime('%B %d, %Y'),
    )


# =============================================================================
# CLI COMMANDS
# =============================================================================

def cmd_build(md_path: str, no_index: bool = False):
    """Build an essay from markdown."""
    md_file = Path(md_path)
    if not md_file.exists():
        print(f"Error: File not found: {md_path}")
        sys.exit(1)
    
    print(f"Building: {md_file.name}")
    
    html, output_path, essay = build_essay_html(md_file)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  → {output_path}")
    
    # Update cache
    essays = load_essays_cache()
    essays[essay.filename] = essay
    save_essays_cache(essays)
    print(f"  → Updated essay cache ({len(essays)} total)")
    
    # Update index
    if not no_index:
        index_html = generate_index_page(essays)
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(index_html)
        print(f"  → Regenerated {INDEX_FILE}")
    
    # Note about definitions
    if essay.definitions:
        print(f"  ℹ  {len(essay.definitions)} definition(s) specified - add manually to definitions.html")


def cmd_rebuild_index():
    """Rebuild index from cached essays."""
    essays = load_essays_cache()
    if not essays:
        print("No essays in cache. Build some essays first with:")
        print("  python build_wiki.py build your-essay.md")
        return
    
    print(f"Rebuilding index from {len(essays)} cached essays...")
    
    index_html = generate_index_page(essays)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"  → {INDEX_FILE}")


def cmd_list_topics():
    """List all topics with counts."""
    essays = load_essays_cache()
    
    by_topic = {}
    for essay in essays.values():
        by_topic[essay.topic] = by_topic.get(essay.topic, 0) + 1
    
    print(f"\nTopics ({len(essays)} total essays):\n")
    for topic_id, topic_name in TOPIC_ORDER:
        count = by_topic.get(topic_id, 0)
        marker = "●" if count > 0 else "○"
        print(f"  {marker} {topic_id}: {topic_name} ({count})")
    
    # Unconfigured topics
    unknown = [t for t in by_topic if t not in TOPIC_MAP]
    if unknown:
        print(f"\n  ⚠ Unconfigured topics: {', '.join(unknown)}")
        print("    Add these to TOPIC_ORDER in build_wiki.py")


def cmd_list_essays():
    """List all essays in cache."""
    essays = load_essays_cache()
    if not essays:
        print("No essays in cache.")
        return
    
    print(f"\nCached essays ({len(essays)}):\n")
    for filename, essay in sorted(essays.items(), key=lambda x: x[1].date, reverse=True):
        print(f"  {essay.date.strftime('%Y-%m-%d')} [{essay.type}] {essay.title}")
        print(f"             → {filename} (topic: {essay.topic})")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='H. Aslan Wiki Build System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python build_wiki.py build essay.md      Build essay and update index
  python build_wiki.py rebuild-index       Regenerate index from cache
  python build_wiki.py list-topics         Show topic breakdown
  python build_wiki.py list-essays         Show all cached essays
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command')
    
    # build
    build_p = subparsers.add_parser('build', help='Build essay from markdown')
    build_p.add_argument('input', help='Markdown file to build')
    build_p.add_argument('--no-index', action='store_true', help='Skip index regeneration')
    
    # rebuild-index
    subparsers.add_parser('rebuild-index', help='Rebuild index from cache')
    
    # list-topics
    subparsers.add_parser('list-topics', help='Show topics and counts')
    
    # list-essays  
    subparsers.add_parser('list-essays', help='Show all cached essays')
    
    args = parser.parse_args()
    
    if args.command == 'build':
        cmd_build(args.input, args.no_index)
    elif args.command == 'rebuild-index':
        cmd_rebuild_index()
    elif args.command == 'list-topics':
        cmd_list_topics()
    elif args.command == 'list-essays':
        cmd_list_essays()
    elif len(sys.argv) > 1 and sys.argv[1].endswith('.md'):
        # Convenience: python build_wiki.py essay.md
        cmd_build(sys.argv[1])
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
