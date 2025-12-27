#!/usr/bin/env python3
"""
H. Aslan Wiki Build Script
Generates topic-based index pages in the Gwern style.

"Not a tame lion."

Usage:
    python build_wiki.py [--config CONFIG_FILE] [--output OUTPUT_DIR]
"""

import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from html.parser import HTMLParser
import html

# ============================================
# CONFIGURATION
# ============================================

DEFAULT_CONFIG = {
    "site_title": "H. Aslan",
    "site_tagline": "Not a tame lion.",
    "base_url": "https://haslan.xyz",
    "content_dir": "pages",
    "output_dir": ".",
    "template_dir": "templates",
    
    # Topic categories for organizing content
    "topics": {
        "consciousness": {
            "title": "Consciousness & Awareness",
            "description": "Explorations of the nature of consciousness, witness-self, and awareness.",
            "keywords": ["consciousness", "awareness", "witness", "observer", "phenomenal", "qualia"]
        },
        "philosophy": {
            "title": "Philosophy & Metaphysics", 
            "description": "Philosophical investigations into the nature of reality, knowledge, and existence.",
            "keywords": ["philosophy", "metaphysics", "epistemology", "ontology", "being"]
        },
        "eastern": {
            "title": "Eastern Traditions",
            "description": "Insights from Vedanta, Buddhism, Taoism, and other Eastern wisdom traditions.",
            "keywords": ["vedanta", "buddhism", "taoism", "gita", "upanishad", "zen", "dharma", "karma"]
        },
        "ai-ethics": {
            "title": "AI & Machine Ethics",
            "description": "Considerations on artificial intelligence, machine consciousness, and digital ethics.",
            "keywords": ["ai", "artificial intelligence", "machine", "robot", "digital", "algorithm"]
        },
        "narrative": {
            "title": "Narrative & Sovereignty",
            "description": "Essays on storytelling, meaning-making, and narrative autonomy.",
            "keywords": ["narrative", "story", "meaning", "sovereignty", "autonomy", "myth"]
        },
        "creative": {
            "title": "Creative Writing",
            "description": "Fiction, poetry, and experimental forms.",
            "keywords": ["fiction", "poetry", "story", "creative", "verse"]
        },
        "technical": {
            "title": "Technical Notes",
            "description": "Programming, systems, and technical documentation.",
            "keywords": ["code", "programming", "technical", "system", "software", "web"]
        },
        "misc": {
            "title": "Miscellaneous",
            "description": "Other writings that don't fit neatly elsewhere.",
            "keywords": []
        }
    },
    
    # Content type badges
    "content_types": {
        "essay": {"label": "Essay", "class": "badge-essay"},
        "sketch": {"label": "Sketch", "class": "badge-sketch"},
        "fiction": {"label": "Fiction", "class": "badge-fiction"},
        "verse": {"label": "Verse", "class": "badge-verse"},
        "note": {"label": "Note", "class": "badge-note"},
        "draft": {"label": "Draft", "class": "badge-draft"},
        "technical": {"label": "Technical", "class": "badge-technical"}
    }
}


# ============================================
# HTML METADATA PARSER
# ============================================

class MetadataParser(HTMLParser):
    """Extract metadata from HTML files."""
    
    def __init__(self):
        super().__init__()
        self.metadata = {}
        self.in_title = False
        self.in_meta_block = False
        self.current_tag = None
        self.title_content = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'title':
            self.in_title = True
            
        elif tag == 'meta':
            name = attrs_dict.get('name', '')
            content = attrs_dict.get('content', '')
            
            if name == 'description':
                self.metadata['description'] = content
            elif name == 'keywords':
                self.metadata['keywords'] = [k.strip() for k in content.split(',')]
            elif name == 'author':
                self.metadata['author'] = content
            elif name == 'date' or name == 'created':
                self.metadata['date'] = content
            elif name == 'modified':
                self.metadata['modified'] = content
            elif name == 'type' or name == 'content-type':
                self.metadata['type'] = content
            elif name == 'topic' or name == 'category':
                self.metadata['topic'] = content
            elif name == 'status':
                self.metadata['status'] = content
            elif name == 'epistemic':
                self.metadata['epistemic'] = content
                
    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
            self.metadata['title'] = ''.join(self.title_content).strip()
            
    def handle_data(self, data):
        if self.in_title:
            self.title_content.append(data)


def extract_metadata(filepath):
    """Extract metadata from an HTML file."""
    parser = MetadataParser()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            parser.feed(content)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return {}
    
    # Add file-based metadata
    stat = os.stat(filepath)
    parser.metadata['filepath'] = str(filepath)
    parser.metadata['filename'] = os.path.basename(filepath)
    parser.metadata['url'] = '/' + str(filepath).replace('\\', '/')
    
    if 'date' not in parser.metadata:
        parser.metadata['date'] = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
    
    if 'title' not in parser.metadata:
        # Try to extract from first h1
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        if h1_match:
            parser.metadata['title'] = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
        else:
            parser.metadata['title'] = os.path.splitext(os.path.basename(filepath))[0].replace('-', ' ').title()
    
    return parser.metadata


# ============================================
# TOPIC CLASSIFICATION
# ============================================

def classify_topic(metadata, topics_config):
    """Determine the best topic for a piece of content."""
    
    # If explicitly set, use that
    if 'topic' in metadata and metadata['topic'] in topics_config:
        return metadata['topic']
    
    # Build a score for each topic based on keyword matches
    scores = defaultdict(int)
    
    # Text to search for keywords
    search_text = ' '.join([
        metadata.get('title', ''),
        metadata.get('description', ''),
        ' '.join(metadata.get('keywords', [])),
        metadata.get('filepath', '')
    ]).lower()
    
    for topic_id, topic_config in topics_config.items():
        for keyword in topic_config.get('keywords', []):
            if keyword.lower() in search_text:
                scores[topic_id] += 1
    
    # Return highest scoring topic, or 'misc' if no matches
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return 'misc'


# ============================================
# INDEX GENERATION
# ============================================

def generate_topic_index(pages_by_topic, config):
    """Generate a topic-based index page."""
    
    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'    <title>Writing Index | {config["site_title"]}</title>',
        '    <meta name="description" content="A topical index of all writings.">',
        '    <link rel="stylesheet" href="/assets/css/style.css">',
        '</head>',
        '<body>',
        '    <a href="#main-content" class="skip-link">Skip to content</a>',
        '',
        '    <!-- Include navigation -->',
        '    <nav id="sidenav" class="sidenav">',
        '        <!-- Nav content loaded separately -->',
        '    </nav>',
        '',
        '    <main id="main-content" class="main-content">',
        '        <article class="entry">',
        '            <header class="entry-header">',
        f'                <h1>Writing Index</h1>',
        '                <p class="entry-subtitle">A topical organization of essays, notes, and creative works.</p>',
        '            </header>',
        '',
        '            <div class="entry-content">',
        '',
        '                <!-- Table of Contents -->',
        '                <nav class="toc toc-index">',
        '                    <h2>Topics</h2>',
        '                    <ul class="toc-grid">',
    ]
    
    # Generate TOC
    for topic_id, topic_config in config['topics'].items():
        if topic_id in pages_by_topic and pages_by_topic[topic_id]:
            count = len(pages_by_topic[topic_id])
            html_parts.append(f'                        <li><a href="#topic-{topic_id}">{topic_config["title"]}</a> <span class="count">({count})</span></li>')
    
    html_parts.extend([
        '                    </ul>',
        '                </nav>',
        '',
    ])
    
    # Generate topic sections
    for topic_id, topic_config in config['topics'].items():
        pages = pages_by_topic.get(topic_id, [])
        if not pages:
            continue
            
        # Sort pages by date (newest first)
        pages.sort(key=lambda p: p.get('date', ''), reverse=True)
        
        html_parts.extend([
            f'                <section class="topic-section" id="topic-{topic_id}">',
            f'                    <h2>{topic_config["title"]}</h2>',
            f'                    <p class="topic-description">{topic_config["description"]}</p>',
            '                    <ul class="writing-list">',
        ])
        
        for page in pages:
            title = html.escape(page.get('title', 'Untitled'))
            url = page.get('url', '#')
            description = html.escape(page.get('description', ''))
            date = page.get('date', '')
            content_type = page.get('type', 'note')
            status = page.get('status', '')
            
            badge_config = config['content_types'].get(content_type, config['content_types']['note'])
            badge_class = badge_config['class']
            badge_label = badge_config['label']
            
            status_class = f' status-{status}' if status else ''
            
            html_parts.extend([
                f'                        <li class="writing-entry{status_class}">',
                f'                            <a href="{url}" class="entry-link">',
                f'                                <span class="entry-title">{title}</span>',
                f'                                <span class="badge {badge_class}">{badge_label}</span>',
            ])
            
            if date:
                html_parts.append(f'                                <time class="entry-date" datetime="{date}">{date}</time>')
                
            html_parts.append('                            </a>')
            
            if description:
                html_parts.append(f'                            <p class="entry-description">{description}</p>')
                
            html_parts.extend([
                '                        </li>',
            ])
        
        html_parts.extend([
            '                    </ul>',
            '                </section>',
            '',
        ])
    
    html_parts.extend([
        '            </div>',
        '        </article>',
        '    </main>',
        '',
        '    <script src="/assets/js/script.js"></script>',
        '</body>',
        '</html>',
    ])
    
    return '\n'.join(html_parts)


def generate_recent_updates(all_pages, config, limit=10):
    """Generate a recent updates section."""
    
    # Sort all pages by modified date or date
    sorted_pages = sorted(
        all_pages,
        key=lambda p: p.get('modified', p.get('date', '')),
        reverse=True
    )[:limit]
    
    html_parts = [
        '<section class="recent-updates">',
        '    <h2>Recent Updates</h2>',
        '    <ul class="updates-list">',
    ]
    
    for page in sorted_pages:
        title = html.escape(page.get('title', 'Untitled'))
        url = page.get('url', '#')
        date = page.get('modified', page.get('date', ''))
        
        html_parts.append(f'        <li><a href="{url}">{title}</a> <time datetime="{date}">{date}</time></li>')
    
    html_parts.extend([
        '    </ul>',
        '</section>',
    ])
    
    return '\n'.join(html_parts)


# ============================================
# SITEMAP GENERATION
# ============================================

def generate_sitemap(all_pages, config):
    """Generate an XML sitemap."""
    
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    
    for page in all_pages:
        url = config['base_url'] + page.get('url', '')
        lastmod = page.get('modified', page.get('date', ''))
        
        xml_parts.extend([
            '    <url>',
            f'        <loc>{html.escape(url)}</loc>',
        ])
        
        if lastmod:
            xml_parts.append(f'        <lastmod>{lastmod}</lastmod>')
            
        xml_parts.append('    </url>')
    
    xml_parts.append('</urlset>')
    
    return '\n'.join(xml_parts)


# ============================================
# JSON INDEX GENERATION
# ============================================

def generate_json_index(pages_by_topic, config):
    """Generate a JSON index for client-side search."""
    
    index = {
        'generated': datetime.now().isoformat(),
        'site': config['site_title'],
        'topics': {},
        'pages': []
    }
    
    for topic_id, pages in pages_by_topic.items():
        topic_config = config['topics'].get(topic_id, {})
        index['topics'][topic_id] = {
            'title': topic_config.get('title', topic_id),
            'description': topic_config.get('description', ''),
            'count': len(pages)
        }
        
        for page in pages:
            index['pages'].append({
                'title': page.get('title', ''),
                'url': page.get('url', ''),
                'description': page.get('description', ''),
                'keywords': page.get('keywords', []),
                'topic': topic_id,
                'type': page.get('type', 'note'),
                'date': page.get('date', ''),
            })
    
    return json.dumps(index, indent=2)


# ============================================
# MAIN BUILD PROCESS
# ============================================

def find_content_files(content_dir):
    """Find all HTML content files."""
    
    content_path = Path(content_dir)
    if not content_path.exists():
        print(f"Content directory not found: {content_dir}")
        return []
    
    files = []
    for ext in ['*.html', '*.htm']:
        files.extend(content_path.rglob(ext))
    
    # Exclude templates, includes, and special files
    exclude_patterns = ['_', 'template', 'include', 'partial', 'index']
    files = [
        f for f in files 
        if not any(p in f.name.lower() for p in exclude_patterns)
    ]
    
    return files


def build_wiki(config):
    """Main build process."""
    
    print(f"Building wiki index...")
    print(f"Content directory: {config['content_dir']}")
    
    # Find all content files
    content_files = find_content_files(config['content_dir'])
    print(f"Found {len(content_files)} content files")
    
    # Extract metadata from each file
    all_pages = []
    for filepath in content_files:
        metadata = extract_metadata(filepath)
        if metadata:
            all_pages.append(metadata)
    
    print(f"Extracted metadata from {len(all_pages)} pages")
    
    # Classify pages by topic
    pages_by_topic = defaultdict(list)
    for page in all_pages:
        topic = classify_topic(page, config['topics'])
        page['_topic'] = topic
        pages_by_topic[topic].append(page)
    
    # Print topic distribution
    print("\nTopic distribution:")
    for topic_id, pages in sorted(pages_by_topic.items()):
        print(f"  {topic_id}: {len(pages)} pages")
    
    # Generate outputs
    output_dir = Path(config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate topic index
    index_html = generate_topic_index(pages_by_topic, config)
    index_path = output_dir / 'writing-index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"\nGenerated: {index_path}")
    
    # Generate JSON index for search
    json_index = generate_json_index(pages_by_topic, config)
    json_path = output_dir / 'search-index.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json_index)
    print(f"Generated: {json_path}")
    
    # Generate sitemap
    sitemap_xml = generate_sitemap(all_pages, config)
    sitemap_path = output_dir / 'sitemap.xml'
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(sitemap_xml)
    print(f"Generated: {sitemap_path}")
    
    print("\nBuild complete!")
    return pages_by_topic


# ============================================
# CLI
# ============================================

def main():
    parser = argparse.ArgumentParser(description='Build H. Aslan wiki index')
    parser.add_argument('--config', '-c', help='Path to config JSON file')
    parser.add_argument('--content', '-d', help='Content directory', default='pages')
    parser.add_argument('--output', '-o', help='Output directory', default='.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without writing files')
    
    args = parser.parse_args()
    
    # Load config
    config = DEFAULT_CONFIG.copy()
    
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            custom_config = json.load(f)
            config.update(custom_config)
    
    if args.content:
        config['content_dir'] = args.content
    if args.output:
        config['output_dir'] = args.output
    
    if args.dry_run:
        print("DRY RUN - no files will be written")
        config['output_dir'] = '/dev/null'
    
    # Build
    build_wiki(config)


if __name__ == '__main__':
    main()
