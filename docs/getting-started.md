# Getting Started

## Installation

### Basic Installation

Install the core library (lightweight, only local storage):

```bash
pip install docu-crawler
```

### Optional Dependencies

Install additional features as needed:

```bash
# YAML configuration support
pip install docu-crawler[yaml]

# AWS S3 Storage
pip install docu-crawler[s3]

# Google Cloud Storage
pip install docu-crawler[gcs]

# Azure Blob Storage
pip install docu-crawler[azure]

# SFTP Storage
pip install docu-crawler[sftp]

# Install everything
pip install docu-crawler[all]
```

## Quick Start

### Using the CLI

The simplest way to use DocuCrawler is via the command line:

```bash
docu-crawler https://docs.example.com
```

This will:
1. Crawl `https://docs.example.com`
2. Download all pages under that path
3. Convert them to Markdown
4. Save them to the `downloaded_docs` directory

### Using Python

You can also use it as a library in your Python scripts:

```python
from docu_crawler import crawl_to_local

# Simple crawl
crawl_to_local("https://docs.example.com", output_dir="my-docs")
```

## Your First Crawl

Let's try a more advanced example. Suppose you want to crawl a documentation site, combine everything into a single file for an LLM, and be polite with a 2-second delay.

**CLI Command:**

```bash
docu-crawler https://docs.python.org/3/ \
  --output python-docs \
  --delay 2.0 \
  --single-file \
  --frontmatter
```

**Python Script:**

```python
from docu_crawler import DocuCrawler

crawler = DocuCrawler(
    start_url="https://docs.python.org/3/",
    output_dir="python-docs",
    delay=2.0,
    single_file=True
)

crawler.crawl()
```

This will create a `documentation.md` file in the `python-docs` directory containing the entire crawled documentation.

