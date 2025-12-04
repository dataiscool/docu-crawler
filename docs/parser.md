# HTML to Markdown Parser

DocuCrawler features a sophisticated HTML-to-Markdown converter specifically optimized for documentation sites.

## How It Works

Unlike generic converters, our parser:
1. **Identifies Main Content**: Smartly detects the documentation body using 20+ common selectors (e.g., `main`, `article`, `.content`, `#docs`).
2. **Cleans Noise**: Removes navigation bars, footers, sidebars, ads, and scripts.
3. **Preserves Structure**: Maintains headings, lists, code blocks, tables, and formatting.
4. **Optimizes for LLMs**: Cleans up excessive whitespace and empty links.

## Configuration Options

You can customize the parser behavior via the Python API using `HtmlProcessorConfig`.

```python
from docu_crawler.processors.config import HtmlProcessorConfig

config = HtmlProcessorConfig(
    ignore_links=False,           # Keep links
    ignore_images=False,          # Keep images
    body_width=0,                 # No text wrapping
    dash_unordered_list=True,     # Use - instead of *
    google_doc=False,             # Enable Google Docs specific cleaning
    single_file=True,             # Combine output
    include_frontmatter=True      # Add metadata headers
)
```

## Frontmatter Support

When `--frontmatter` is enabled, each Markdown file gets a YAML header. This is critical for RAG systems to know the source and title of the content.

**Example Output**:
```markdown
---
title: "Installation Guide"
source: "https://docs.example.com/install"
date: 2025-10-27
---

# Installation Guide

Content follows...
```

## Google Docs Support

If you are crawling published Google Docs, enable `google_doc=True` (or modify source code config). This handles specific Google Docs HTML quirks like bold/italic styling classes.

## Token Optimization

The parser automatically post-processes Markdown to be "token-efficient" for LLMs:
- Removes empty links `[]()`
- Removes images without alt text `![]()`
- Consolidates multiple newlines
- Fixes list spacing

