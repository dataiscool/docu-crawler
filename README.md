# docu-crawler

> A lightweight, extensible Python library for crawling websites and converting HTML content to Markdown format. Perfect for documentation extraction, content migration, offline reading, and SEO optimization.

**docu-crawler** is a powerful yet lightweight web crawler library that helps you extract, convert, and store web content efficiently. Whether you're building documentation sites, migrating content, or creating offline documentation, docu-crawler provides a simple, flexible solution with minimal dependencies.

## What is docu-crawler?

docu-crawler is a Python library designed for:
- **Web Crawling**: Crawl websites systematically while respecting robots.txt
- **HTML to Markdown Conversion**: Convert HTML pages to clean, readable Markdown
- **Content Extraction**: Extract and preserve website structure and content
- **Multi-Cloud Storage**: Store crawled content locally or in cloud storage (S3, GCS, Azure, SFTP)
- **SEO Optimization**: Generate sitemaps, extract metadata, and create SEO-friendly content

## Why use docu-crawler?

- ✅ **Minimal Dependencies**: Only requires `requests` and `beautifulsoup4` for core functionality
- ✅ **Easy to Use**: Simple API and CLI interface
- ✅ **Production Ready**: Built-in retry logic, rate limiting, and error handling
- ✅ **Extensible**: Plugin-based storage system, easy to add custom backends
- ✅ **SEO Friendly**: Generates sitemaps, extracts metadata, preserves structure
- ✅ **Cross-Platform**: Works on Linux, Windows, and macOS

## Features

- 🚀 **Lightweight**: Minimal dependencies (only `requests` and `beautifulsoup4` required)
- ☁️ **Multi-Cloud Storage**: Support for local filesystem, AWS S3, Google Cloud Storage, Azure Blob Storage, and SFTP
- 🔄 **Flexible API**: Use as a library or CLI tool
- 📝 **HTML to Markdown**: Intelligent conversion preserving structure and formatting
- 🤖 **Robots.txt Support**: Respects robots.txt and crawl-delay directives
- ⚡ **Performance**: Configurable rate limiting and retry logic
- 🔍 **SEO Optimized**: Generates sitemaps, extracts metadata, and adds frontmatter
- 🛡️ **Cross-Platform**: Works on Linux, Windows, and macOS
- 📦 **Optional Dependencies**: Install only what you need

## Installation

### Basic Installation

```bash
pip install docu-crawler
```

This installs only the core dependencies (`requests` and `beautifulsoup4`).

### With Optional Features

```bash
# With YAML config file support
pip install docu-crawler[yaml]

# With specific storage backend
pip install docu-crawler[s3]      # AWS S3
pip install docu-crawler[gcs]     # Google Cloud Storage
pip install docu-crawler[azure]    # Azure Blob Storage
pip install docu-crawler[sftp]     # SFTP

# With async support (for advanced use cases)
pip install docu-crawler[async]

# Install everything
pip install docu-crawler[all]
```

## Quick Start

### As a Python Library

```python
from docu_crawler import crawl_to_local

# Simple one-liner
result = crawl_to_local("https://docs.example.com", output_dir="my_docs")
print(f"Crawled {result['pages_crawled']} pages")
```

### As a CLI Tool

```bash
# Basic usage
docu-crawler https://docs.example.com

# With options
docu-crawler https://docs.example.com --output my-docs --delay 2 --max-pages 100
```

## Usage Examples

### Python API

#### Basic Crawling

```python
from docu_crawler import DocuCrawler

# Create crawler instance
crawler = DocuCrawler(
    start_url="https://docs.example.com",
    output_dir="downloaded_docs",
    delay=1.0,
    max_pages=100
)

# Start crawling
crawler.crawl()
```

#### Crawl to Cloud Storage

```python
from docu_crawler import crawl_to_s3, crawl_to_gcs, crawl_to_azure, crawl_to_sftp

# AWS S3
result = crawl_to_s3(
    url="https://docs.example.com",
    bucket="my-bucket",
    region="us-east-1"
)

# Google Cloud Storage
result = crawl_to_gcs(
    url="https://docs.example.com",
    bucket="my-bucket",
    project="my-project"
)

# Azure Blob Storage
result = crawl_to_azure(
    url="https://docs.example.com",
    container="my-container",
    connection_string="DefaultEndpointsProtocol=https;..."
)

# SFTP
result = crawl_to_sftp(
    url="https://docs.example.com",
    host="sftp.example.com",
    user="username",
    password="password"  # or use key_file parameter
)
```

#### Advanced Usage with Callbacks

```python
from docu_crawler import crawl

def on_page_crawled(url, page_count):
    print(f"Page {page_count}: {url}")

def on_error(url, error):
    print(f"Error crawling {url}: {error}")

result = crawl(
    url="https://docs.example.com",
    output_dir="my_docs",
    on_page_crawled=on_page_crawled,
    on_error=on_error
)
```

### CLI Usage

#### Basic Options

```bash
# Basic crawl
docu-crawler https://docs.example.com

# Specify output directory
docu-crawler https://docs.example.com --output my-docs

# Set delay between requests
docu-crawler https://docs.example.com --delay 2.0

# Limit number of pages
docu-crawler https://docs.example.com --max-pages 50

# Set timeout
docu-crawler https://docs.example.com --timeout 30

# Set log level
docu-crawler https://docs.example.com --log-level DEBUG
```

#### Storage Backends

```bash
# Local storage (default)
docu-crawler https://docs.example.com --storage-type local --output my-docs

# AWS S3
docu-crawler https://docs.example.com --storage-type s3 --s3-bucket my-bucket --s3-region us-east-1

# Google Cloud Storage
docu-crawler https://docs.example.com --storage-type gcs --bucket my-bucket --project my-project

# Azure Blob Storage
docu-crawler https://docs.example.com --storage-type azure --azure-container my-container

# SFTP
docu-crawler https://docs.example.com --storage-type sftp --sftp-host sftp.example.com --sftp-user username
```

#### Using Configuration File

Create `crawler_config.yaml`:

```yaml
url: https://docs.example.com
output: downloaded_docs
delay: 1.0
max_pages: 0
timeout: 10
log_level: INFO

# Storage configuration
storage_type: s3
s3_bucket: my-bucket
s3_region: us-east-1
```

Then run:

```bash
docu-crawler  # Loads from config file automatically
```

## Storage Backends

### Local Filesystem (Default)

No additional dependencies required. Files are saved to the specified output directory.

```python
from docu_crawler import crawl_to_local

result = crawl_to_local("https://docs.example.com", output_dir="docs")
```

### AWS S3

Requires: `pip install docu-crawler[s3]`

```python
from docu_crawler import crawl_to_s3

result = crawl_to_s3(
    url="https://docs.example.com",
    bucket="my-bucket",
    region="us-east-1"
)
```

Credentials can be provided via:
- Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`
- AWS credentials file: `~/.aws/credentials`
- IAM roles (if running on EC2)

### Google Cloud Storage

Requires: `pip install docu-crawler[gcs]`

```python
from docu_crawler import crawl_to_gcs

result = crawl_to_gcs(
    url="https://docs.example.com",
    bucket="my-bucket",
    project="my-project",
    credentials="/path/to/credentials.json"  # Optional
)
```

Credentials can be provided via:
- `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- Service account key file
- Application Default Credentials

### Azure Blob Storage

Requires: `pip install docu-crawler[azure]`

```python
from docu_crawler import crawl_to_azure

result = crawl_to_azure(
    url="https://docs.example.com",
    container="my-container",
    connection_string="DefaultEndpointsProtocol=https;..."  # Optional
)
```

Credentials can be provided via:
- `AZURE_STORAGE_CONNECTION_STRING` environment variable
- Connection string parameter
- Account name and key

### SFTP

Requires: `pip install docu-crawler[sftp]`

```python
from docu_crawler import crawl_to_sftp

result = crawl_to_sftp(
    url="https://docs.example.com",
    host="sftp.example.com",
    user="username",
    password="password",  # or key_file="/path/to/key"
    port=22,
    remote_path="/remote/path"
)
```

## API Reference

### Main Classes

#### `DocuCrawler`

Main crawler class for programmatic use.

```python
from docu_crawler import DocuCrawler

crawler = DocuCrawler(
    start_url: str,
    output_dir: str = "downloaded_docs",
    delay: float = 1.0,
    max_pages: int = 0,
    timeout: int = 10,
    storage_config: Optional[Dict[str, Any]] = None
)

crawler.crawl()
```

### Convenience Functions

#### `crawl()`

General-purpose crawl function with callbacks.

```python
from docu_crawler import crawl

result = crawl(
    url: str,
    output_dir: str = "downloaded_docs",
    delay: float = 1.0,
    max_pages: int = 0,
    timeout: int = 10,
    storage_config: Optional[Dict[str, Any]] = None,
    on_page_crawled: Optional[Callable[[str, int], None]] = None,
    on_error: Optional[Callable[[str, Exception], None]] = None
) -> Dict[str, Any]
```

#### Storage-Specific Functions

- `crawl_to_local(url, output_dir, **kwargs)`
- `crawl_to_s3(url, bucket, region=None, **kwargs)`
- `crawl_to_gcs(url, bucket, project=None, credentials=None, **kwargs)`
- `crawl_to_azure(url, container, connection_string=None, **kwargs)`
- `crawl_to_sftp(url, host, user, password=None, port=22, key_file=None, remote_path='', **kwargs)`

## Configuration

### Environment Variables

All storage backends support environment variables for credentials:

- **AWS S3**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`
- **GCS**: `GOOGLE_APPLICATION_CREDENTIALS`
- **Azure**: `AZURE_STORAGE_CONNECTION_STRING`
- **SFTP**: `SFTP_PASSWORD`, `SFTP_KEY_FILE`

### Configuration File

Create a YAML configuration file (requires `docu-crawler[yaml]`):

```yaml
# Target URL
url: https://docs.example.com

# Output settings
output: downloaded_docs

# Crawler behavior
delay: 1.0
max_pages: 0  # 0 for unlimited
timeout: 10
log_level: INFO

# Storage configuration
storage_type: s3  # local, gcs, s3, azure, sftp
s3_bucket: my-bucket
s3_region: us-east-1
```

The crawler looks for config files in:
1. `./crawler_config.yaml`
2. `./config/crawler_config.yaml`
3. `~/.config/docu-crawler/config.yaml`
4. `/etc/docu-crawler/config.yaml`

## Advanced Features

### SEO Optimization

docu-crawler includes comprehensive SEO features to help your crawled content rank better in search engines:

- **Metadata Extraction**: Automatically extracts title, description, keywords, and Open Graph tags from HTML
- **Frontmatter Support**: Adds YAML frontmatter to generated Markdown files with metadata
- **Sitemap Generation**: Creates `sitemap.xml` files for crawled content to help search engines index your pages
- **Structured Data**: Preserves JSON-LD and microdata from source pages
- **Canonical URLs**: Maintains canonical URL references for proper SEO
- **Semantic HTML**: Preserves semantic structure in Markdown output

Example of SEO-optimized output:

```markdown
---
title: Getting Started with Python
description: Learn how to get started with Python programming
canonical: https://docs.example.com/getting-started
keywords: python, programming, tutorial
---

# Getting Started with Python

Content here...
```

### Robots.txt Support

Automatically respects `robots.txt` files:

```python
from docu_crawler import DocuCrawler
from docu_crawler.utils.robots import RobotsTxtChecker

robots_checker = RobotsTxtChecker()
if robots_checker.can_fetch(url):
    # Crawl the URL
    pass
```

### Rate Limiting

Built-in rate limiting support:

```python
from docu_crawler.utils.rate_limiter import RateLimiter

limiter = RateLimiter(rate=10, per=60)  # 10 requests per minute
limiter.wait_if_needed(domain="example.com")
```

### Retry Logic

Automatic retry with exponential backoff:

```python
from docu_crawler.utils.retry import retry_with_backoff

@retry_with_backoff(max_retries=3, initial_delay=1.0)
def fetch_url(url):
    # Your code here
    pass
```

## Project Structure

```
docu-crawler/
├── src/
│   ├── api/              # Public API
│   │   ├── __init__.py   # Main API exports
│   │   └── simple.py     # Convenience functions
│   ├── models/           # Data models
│   │   ├── crawler_stats.py
│   │   └── crawl_result.py
│   ├── processors/       # Content processors
│   │   └── html_processor.py
│   ├── utils/            # Utilities
│   │   ├── storage/      # Storage backends
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   ├── gcs.py
│   │   │   ├── aws_s3.py
│   │   │   ├── azure_blob.py
│   │   │   └── sftp.py
│   │   ├── cli.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── robots.py
│   │   ├── retry.py
│   │   ├── rate_limiter.py
│   │   └── sitemap.py
│   ├── cli.py            # CLI entry point
│   └── doc_crawler.py    # Main crawler class
├── crawler_config.yaml.example
├── setup.py
└── README.md
```

## Troubleshooting

### Common Issues

**Import Error**: Make sure you've installed docu-crawler:
```bash
pip install docu-crawler
```

**Storage Backend Error**: Install the required storage backend:
```bash
pip install docu-crawler[s3]  # or gcs, azure, sftp
```

**YAML Config Error**: Install YAML support:
```bash
pip install docu-crawler[yaml]
```

**SSL Certificate Error**: Some sites may have SSL issues. The crawler uses proper SSL verification by default.

## Contributing

Contributions are welcome! Whether it's bug fixes, new features, or documentation improvements, we appreciate your help.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links and Resources

- **GitHub Repository**: https://github.com/dataiscool/docu-crawler
- **PyPI Package**: https://pypi.org/project/docu-crawler/ (once published)
- **Issue Tracker**: https://github.com/dataiscool/docu-crawler/issues
- **Documentation**: See `docs/` directory for detailed API documentation

## Support

- **Questions**: Open an issue on GitHub
- **Bugs**: Report bugs via GitHub Issues
- **Feature Requests**: Submit feature requests via GitHub Issues

## Use Cases

### Documentation Sites
Crawl and convert documentation websites to Markdown for offline reading or migration.

### Content Migration
Migrate content from one platform to another by converting HTML to Markdown.

### SEO Tools
Generate sitemaps and extract metadata for SEO optimization.

### Offline Documentation
Create offline versions of online documentation for local access.

### Content Analysis
Extract and analyze web content programmatically.

## Frequently Asked Questions (FAQ)

### How do I install docu-crawler?

```bash
pip install docu-crawler
```

For optional features like cloud storage support:
```bash
pip install docu-crawler[all]
```

### What Python versions are supported?

docu-crawler supports Python 3.9 and above.

### Can I use it without cloud storage?

Yes! Local filesystem storage is the default and requires no additional dependencies.

### Does it respect robots.txt?

Yes, docu-crawler automatically respects robots.txt files and crawl-delay directives.

### Can I customize the HTML to Markdown conversion?

Yes, the HTML processor can be extended and customized for your specific needs.

### Is it fast?

docu-crawler is designed for efficiency with configurable rate limiting and retry logic. For maximum performance, consider using the async API (coming soon).

## Related Projects

- [Scrapy](https://scrapy.org/) - Full-featured web scraping framework
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing library
- [Markdownify](https://github.com/matthewwithanm/python-markdownify) - HTML to Markdown converter

## Keywords

web crawler, html to markdown, documentation crawler, content extraction, sitemap generator, seo tools, python crawler, web scraping library, markdown converter, documentation tool, python web crawler, html parser, markdown generator, website crawler, content migration tool, documentation generator, sitemap creator, seo crawler, python scraping library, html to markdown python, web content extractor, documentation site crawler, markdown converter tool, python crawler library, website content extractor
