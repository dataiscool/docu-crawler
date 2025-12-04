# DocuCrawler Documentation

Welcome to the documentation for **DocuCrawler**, a lightweight Python web crawler designed for extracting documentation websites and converting them to Markdown.

## Overview

DocuCrawler is built to be simple, efficient, and perfect for:
- Creating datasets for LLM training or RAG (Retrieval-Augmented Generation) systems.
- Migrating content from legacy HTML documentation to modern Markdown-based systems.
- Creating offline archives of documentation sites.

## Table of Contents

1. [Getting Started](getting-started.md)
   - Installation
   - Quick Start
   - Your First Crawl

2. [Configuration](configuration.md)
   - Configuration File
   - Command Line Arguments
   - Environment Variables

3. [Crawling Features](crawling.md)
   - Robots.txt Respect
   - Sitemap Support
   - Rate Limiting
   - Retry Logic

4. [HTML to Markdown Parser](parser.md)
   - How it works
   - Configuration Options
   - Frontmatter Support
   - Google Docs Support

5. [Storage Backends](storage.md)
   - Local Filesystem
   - AWS S3
   - Google Cloud Storage (GCS)
   - Azure Blob Storage
   - SFTP

6. [Python API Reference](api.md)
   - DocuCrawler Class
   - Convenience Functions
   - Callbacks and Customization

