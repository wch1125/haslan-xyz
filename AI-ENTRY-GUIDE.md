# AI Entry Guide for H. Aslan Wiki

*Instructions for Claude instances working on haslan.xyz*

## Quick Start

You're helping maintain a personal wiki. The owner (Will) writes essays on consciousness, institutional analysis, and other topics. Your job is to help with writing, editing, and converting essays to the site's HTML format.

## Workflow Options

### Option 1: Markdown-First (Preferred)

Write essays in markdown with YAML front matter, then convert using `build_essay.py`:

```bash
python build_essay.py essay-name.md
# Outputs to pages/writing/essay-name.html
```

### Option 2: Direct HTML (Legacy)

Generate HTML directly matching the template structure. Use this only if the markdown converter doesn't support a needed feature.

---

## Markdown Format

### Front Matter

```yaml
---
title: The Title of the Essay
date: 2025-12-27
type: sketch  # essay | sketch | notebook | fiction | draft
abstract: >
  A brief description. Can include [[definition links]].
  Keep under 200 words.
claims_not_making:
  - First disclaimer
  - Second disclaimer
update_triggers:
  - What would change my mind
  - Another condition
---
```

### Content Types

| Type | Badge | Use For |
|------|-------|---------|
| `essay` | Essay | Argued and structured pieces |
| `sketch` | Sketch | Speculative, exploratory |
| `notebook` | Notebook | Working notes, rough |
| `fiction` | Fiction | Creative work |
| `draft` | Draft | Unfinished, WIP |

### Special Syntax

**Definition Links:**
```markdown
[[Conductor]]                -> links to definitions.html#conductor
[[conductor|the witness]]    -> displays "the witness", links to #conductor
```

**Standard Markdown:**
- Headers: `## Section Title` (h2 creates sections with auto-IDs)
- Bold: `**text**`
- Italic: `*text*`
- Code: `` `inline` `` or fenced blocks
- Lists: `-` or `1.`
- Blockquotes: `>`
- Links: `[text](url)`

---

## Site Structure

```
haslan.xyz/
├── index.html                 # Homepage
├── build_essay.py             # Markdown converter
├── wiki-manager.py            # Flask admin tool
├── assets/
│   ├── css/style.css
│   └── js/script.js
└── pages/
    ├── definitions.html       # Glossary (add new terms here)
    ├── creative-writing.html  # Essay index (add cards here)
    ├── quotes.html
    └── writing/
        └── [essays].html      # Individual essays
```

## When Adding a New Essay

1. **Create the essay** in markdown format
2. **Convert to HTML**: `python build_essay.py essay.md`
3. **Add to creative-writing.html**: Insert a card in the appropriate section
4. **Add any new definitions** to definitions.html
5. **Commit**: `git add . && git commit -m "Add: Essay Title" && git push`

## Card Format for creative-writing.html

```html
<div class="writing-card" data-category="sketch">
    <h3><a href="writing/essay-filename.html">Essay Title</a></h3>
    <div class="writing-meta">
        <span class="content-badge badge-sketch">Sketch</span>
        <time datetime="2025-12-27">27 December 2025</time>
    </div>
    <p>One-sentence description of the essay.</p>
</div>
```

## Definition Entry Format

```html
<div class="definition-entry" id="term-id">
    <h3><span class="definition-term">Term Name</span></h3>
    <div class="definition-metadata">
        <span class="definition-letter">T</span>
        <span class="definition-date">Added: December 2025</span>
    </div>
    <div class="definition-content">
        <p>Definition text. Can reference other <a href="#other-term" class="definition-link">Defined Terms</a>.</p>
    </div>
</div>
```

## Style Notes

- **Dropcap**: First paragraph after h2 gets dropcap styling via CSS
- **Sidenotes**: Use sparingly; work on desktop, collapse on mobile
- **Collapsibles**: Good for objections, tangents, detailed examples
- **Definition links**: Use for key terms; don't overlink

## Content Guidelines

The wiki voice is:
- First-person but not confessional
- Intellectually honest (epistemic humility)
- Shows working (acknowledges uncertainty)
- References sources when building on others' work

Each essay should have:
- Clear abstract summarizing the argument
- "What this is not claiming" section (prevents misreading)
- "What would update this" section (shows intellectual honesty)

## Files You'll Commonly Edit

| File | When |
|------|------|
| `pages/writing/*.html` | New essays |
| `pages/creative-writing.html` | Adding essay cards |
| `pages/definitions.html` | New defined terms |
| `pages/quotes.html` | New quotes |

## Common Tasks

**"Convert this essay to HTML"**
→ Use build_essay.py or generate HTML matching template

**"Add this essay to the site"**
→ Create HTML + add card to creative-writing.html + commit

**"Add a new definition"**
→ Add entry to definitions.html in alphabetical position

**"Review/edit existing essay"**
→ Edit the HTML directly, maintain structure

---

## Questions?

If unclear about site conventions, ask Will. When in doubt:
- Match existing essay structure
- Use sketch badge for exploratory work
- Include epistemic disclaimers
- Keep abstracts concise
