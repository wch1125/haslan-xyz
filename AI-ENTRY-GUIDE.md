# AI-Assisted Entry Generation Guide

*For ChatGPT, Claude, or any LLM helping create content for haslan.xyz*

---

## About This Wiki

**haslan.xyz** is a personal wiki written under the pseudonym **H. Aslan**. It uses:

- **Defined Terms** — Capitalized terms that link to a glossary with hover previews
- **Sidenotes** — Tufte-style marginal notes for tangential information
- **Collapsible sections** — Progressive disclosure for detailed content
- **Evergreen pages** — Content that evolves rather than chronological posts

The voice is: **precise, unsentimental, not performative**. Avoid absolute claims unless explicitly warranted. Prefer clarity over cleverness.

---

## Universal Prompt: Generate Entry + Definitions

Copy and paste this prompt at the end of any productive conversation to generate wiki-ready content:

---

### THE PROMPT

```
You are helping me update my personal wiki (haslan.xyz). Use ONLY what we discussed in this chat as source material. Do not invent biographical facts, events, or claims. If something is uncertain, flag it as an assumption and write around it.

**Step 0: Pick an output format**

If I did not explicitly specify a preferred output format in my message, reply with only:

> "Which output format do you want: **A** (copy/paste sections) or **B** (structured fields)?"

Do not generate the entry until I answer.

If I specified a format (A or B), proceed directly.

---

## Output Formats

### Format A: Copy/paste sections

Return your answer in exactly these sections, in this order:

**A) Page metadata**
- Title:
- Proposed filename/slug: (no extension)
- One-sentence description: (for meta / homepage card)
- Abstract: (2–4 sentences)

**B) Page content (HTML-only)**

Write the page content as HTML blocks that can be pasted into the wiki-manager "Add Page" content field or into an HTML template.

Rules:
- Use `<section>` blocks with ids
- Use `<h2>` headings
- Use `<p>`, `<ul>`, `<li>`, `<details class="collapse">` and `<summary>` where appropriate
- Include 2–5 sidenotes in this exact pattern:

```html
<span class="sidenote"><span class="sidenote-number"></span><span class="sidenote-content">…</span></span>
```

- When you use a Defined Term, wrap it as a link like:

```html
<a href="definitions.html#slug" class="definition-link" data-term="Term" data-definition="Short definition">Term</a>
```

(Choose a slug that matches the definition's id.)

**C) Definitions to add (wiki-manager ready)**

For each definition, output in this exact mini-template (repeat per term):

```
Term:
Definition: (1–3 paragraphs; separate paragraphs with a blank line)
Related Terms: (comma-separated term names; you may use Term|note if it clarifies the relationship)
```

Rules:
- Definitions must match the voice: precise, unsentimental, not performative
- Avoid absolute claims ("always," "never") unless explicitly discussed
- Prefer "Not X; rather Y" clarifications when useful

**D) Cross-link map**
- Bullet list of how the definitions relate (A → B → C)
- A short list of where in the page each term should be linked (by section id)

**E) Edits checklist**
- 5–10 bullets of final checks (tone consistency, claim hygiene, link slugs, etc.)

---

### Format B: Structured fields (pasteable object)

Return a single code block containing an object with exactly these keys:

```javascript
{
  "page": {
    "title": "string",
    "slug": "string, no extension",
    "description": "string, one sentence",
    "abstract": "string, 2–4 sentences",
    "content_html": "string: HTML only; same rules as Format A",
    "suggest_add_to_home": boolean,
    "home_card_blurb": "string; can be empty"
  },
  "definitions": [
    {
      "term": "string",
      "id_slug": "string",
      "definition_paragraphs": ["array of strings; 1–3 items"],
      "related_terms": ["array of strings; may include Term|note"],
      "short_definition": "string; 8–20 words, for hover previews"
    }
  ],
  "crosslink_map": {
    "edges": ["array of strings like 'A -> B'"],
    "page_links": [
      { "section_id": "intro", "terms": ["Term1", "Term2"] }
    ]
  },
  "final_checks": ["array of strings"]
}
```

Rules for Format B:
- `content_html` must include the same sidenote pattern and definition-link pattern
- Do not include any keys beyond those listed
- Do not include comments

---

## Content Guidance

- Keep the entry tight: aim for **800–1500 words**
- Use specific examples from our conversation, but avoid names unless necessary
- Make the argument legible without preaching
- Create **0–12 definitions**: only add terms that genuinely do work in the entry

---

**Now generate a new haslan.xyz entry and any supporting definitions based on this chat.**
```

---

## HTML Patterns Reference

### Sidenote
```html
<span class="sidenote">
  <span class="sidenote-number"></span>
  <span class="sidenote-content">Your marginal note here.</span>
</span>
```

### Definition Link
```html
<a href="definitions.html#slug-here" class="definition-link" 
   data-term="Term Name" 
   data-definition="8-20 word definition for hover preview">Term Name</a>
```

### Collapsible Section
```html
<details class="collapse">
  <summary>Click to expand</summary>
  <div class="collapse-content">
    <p>Hidden content here.</p>
  </div>
</details>
```

### Section with ID
```html
<section id="section-name">
  <h2>Section Title</h2>
  <p>Content...</p>
</section>
```

### Dropcap (first paragraph of page)
```html
<p><span class="dropcap">T</span>he rest of the first sentence...</p>
```

### Abstract Block
```html
<div class="abstract">
  <p><span class="abstract-label">Abstract:</span> Your 2-4 sentence summary here.</p>
</div>
```

---

## Definition Entry Template

When adding to `definitions.html`, use this structure:

```html
<div class="definition-entry" id="term-slug">
  <h3><span class="definition-term">Term Name</span></h3>
  <div class="definition-metadata">
    <span class="definition-letter">T</span>
    <span class="definition-date">Added: Month Year</span>
  </div>
  <div class="definition-content">
    <p>First paragraph of definition.</p>
    <p>Second paragraph if needed.</p>
    
    <details class="collapse">
      <summary>Related Concepts</summary>
      <div class="collapse-content">
        <ul>
          <li><a href="#related-term">Related Term</a> (relationship note)</li>
        </ul>
      </div>
    </details>
  </div>
</div>
```

---

## Voice Guidelines

### Do
- Be precise and specific
- Acknowledge uncertainty ("often," "tends to," "in many cases")
- Use "Not X; rather Y" to clarify distinctions
- Ground claims in observable patterns
- Write as if explaining to a curious, intelligent reader

### Don't
- Make absolute claims without warrant
- Preach or moralize
- Perform authenticity (just be direct)
- Invent biographical details
- Over-explain or pad for length

---

## Existing Defined Terms

Before creating new definitions, check if these existing terms cover your concept:

- Algorithmic Mediation
- Authenticity
- Canonical Self
- Conformity
- Context Collapse
- Empathy
- Epistemic Commons
- Epistemic Divergence
- Integrity
- Locus of Verifiable Truth
- Machine Legibility
- Narrative Drift
- Narrative Sovereignty
- Personal Domain
- Primary Artifact
- Provenance
- Public Narrative
- Reality Lens
- Reputation Score
- Self-Awareness
- Shadow Profile

If a term already exists, link to it rather than redefining it.

---

## After Generation

1. Review the output for tone consistency
2. Verify all definition slugs match their `id` attributes
3. Check that `data-definition` attributes are 8-20 words
4. Test sidenote formatting
5. Add the page via wiki-manager or direct HTML
6. Add definitions to `definitions.html`
7. Commit and push:
   ```bash
   git add . && git commit -m "Add: [page title]" && git push
   ```

---

*"Not a tame lion."*
