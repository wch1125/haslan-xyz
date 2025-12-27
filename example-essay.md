---
title: Example Essay Title
date: 2025-12-27
type: sketch
topic: consciousness          # Groups this in the "Consciousness & The Symphony" section
abstract: This is a brief description of what the essay covers. You can include [[definition links]] here that will automatically convert to hover-preview links pointing to your definitions page.
claims_not_making:
  - That this example is comprehensive
  - That the syntax covers all edge cases
  - That you should use this without testing first
update_triggers:
  - Finding bugs in the conversion process
  - Discovering features the template needs that aren't supported
  - Better approaches to any of this
---

## Introduction

This is the first paragraph of the introduction. The first letter after any h2 heading will automatically get the dropcap treatment when rendered.

Here's a second paragraph showing normal text flow. You can write in standard markdown with **bold**, *italics*, and `inline code`.

## Using Definition Links

When you want to reference a defined term, use double brackets: [[Conductor]] or [[Audience]].

If you want custom display text, use the pipe syntax: [[conductor|the witness-self]] will display as "the witness-self" but link to the conductor definition.

This is useful for making prose flow naturally while still connecting to your definitions system.

## Code Blocks

Standard fenced code blocks work:

```python
def example():
    return "This renders as a code block"
```

## Lists and Formatting

Regular markdown lists work as expected:

- First item
- Second item
- Third item with **bold** text

Numbered lists too:

1. First step
2. Second step
3. Third step

## Blockquotes

> This is a blockquote. It will be styled according to your CSS.
> 
> Multiple paragraphs work too.

## Closing

The closing section wraps up the essay. Each h2 section gets wrapped in a `<section>` tag with an auto-generated ID based on the heading text.

This makes it easy to link directly to sections: `#closing` would jump here.
