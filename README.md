# docu-crawler: Python Web Crawler for HTML to Markdown Conversion

[![PyPI version](https://badge.fury.io/py/docu-crawler.svg)](https://badge.fury.io/py/docu-crawler)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Fast, lightweight Python library for crawling websites and converting HTML to Markdown. Perfect for documentation extraction, content migration, and offline reading.**

**docu-crawler** is a production-ready Python web crawler that extracts, converts, and stores web content efficiently. Crawl documentation sites, migrate content, and create offline documentation with minimal dependencies.

**Current Version:** 1.1.0 - See [CHANGELOG.md](CHANGELOG.md) for latest updates and bug fixes.

## What is docu-crawler?

**docu-crawler** is a specialized Python web crawler library designed for:

- **Web Crawling**: Systematically crawl websites while respecting robots.txt
- **HTML to Markdown Conversion**: Convert HTML pages to clean, readable Markdown format
- **Content Extraction**: Extract and preserve website structure and content
- **Multi-Cloud Storage**: Store crawled content locally or in cloud storage (AWS S3, Google Cloud Storage, Azure Blob Storage, SFTP)

## Why Choose docu-crawler?

- **Minimal Dependencies**: Only requires `requests` and `beautifulsoup4` for core functionality
- **Easy to Use**: Simple Python API and CLI interface
- **Production Ready**: Built-in retry logic, rate limiting, and comprehensive error handling
- **Extensible**: Plugin-based storage system, easy to add custom backends
- **Cross-Platform**: Works on Linux, Windows, and macOS
- **Robust**: Extensive bug fixes and improvements in v1.1.0 for stability and reliability

## Key Features

- **Lightweight**: Minimal dependencies (only `requests` and `beautifulsoup4` required)
- **Multi-Cloud Storage**: Support for local filesystem, AWS S3, Google Cloud Storage, Azure Blob Storage, and SFTP
- **Flexible API**: Use as a Python library or CLI tool
- **HTML to Markdown**: Intelligent conversion preserving structure and formatting
- **Robots.txt Support**: Respects robots.txt and crawl-delay directives
- **Sitemap Support**: Automatically detects and crawls pages from sitemap.xml
- **Performance**: Configurable rate limiting and retry logic
- **Cross-Platform**: Works on Linux, Windows, and macOS
- **Optional Dependencies**: Install only what you need

## Installation

### Basic Installation

```bash
pip install docu-crawler
```

This installs only the core dependencies (`requests` and `beautifulsoup4`).

### With Optional Features

```bash
pip install docu-crawler[yaml]      # YAML config file support
pip install docu-crawler[s3]        # AWS S3 storage
pip install docu-crawler[gcs]       # Google Cloud Storage
pip install docu-crawler[azure]     # Azure Blob Storage
pip install docu-crawler[sftp]      # SFTP storage
pip install docu-crawler[all]        # Install everything
```

## Quick Start Guide

### Python Library Usage

```python
from docu_crawler import crawl_to_local

result = crawl_to_local("https://docs.example.com", output_dir="my_docs")
print(f"Crawled {result['pages_crawled']} pages")
```

### Command Line Interface

```bash
docu-crawler https://docs.example.com --output my-docs --delay 2 --max-pages 100 --single-file --frontmatter
```

## Usage Examples

### Basic Web Crawling

```python
from docu_crawler import DocuCrawler

crawler = DocuCrawler(
    start_url="https://docs.example.com",
    output_dir="downloaded_docs",
    delay=1.0,
    max_pages=100
)
crawler.crawl()
```

### Crawl to Cloud Storage

```python
from docu_crawler import crawl_to_s3, crawl_to_gcs, crawl_to_azure, crawl_to_sftp

# AWS S3
crawl_to_s3(url="https://docs.example.com", bucket="my-bucket", region="us-east-1")

# Google Cloud Storage
crawl_to_gcs(url="https://docs.example.com", bucket="my-bucket", project="my-project")

# Azure Blob Storage
crawl_to_azure(url="https://docs.example.com", container="my-container")

# SFTP
crawl_to_sftp(url="https://docs.example.com", host="sftp.example.com", user="username")
```

### Advanced Usage with Callbacks

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

**Note:** Callbacks are now passed directly to the crawler constructor (v1.1.0+), providing better error handling and reliability.

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

Credentials via: Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`), AWS credentials file, or IAM roles.

### Google Cloud Storage

Requires: `pip install docu-crawler[gcs]`

```python
from docu_crawler import crawl_to_gcs

result = crawl_to_gcs(
    url="https://docs.example.com",
    bucket="my-bucket",
    project="my-project"
)
```

Credentials via: `GOOGLE_APPLICATION_CREDENTIALS` environment variable or service account key file.

### Azure Blob Storage

Requires: `pip install docu-crawler[azure]`

```python
from docu_crawler import crawl_to_azure

result = crawl_to_azure(
    url="https://docs.example.com",
    container="my-container"
)
```

Credentials via: `AZURE_STORAGE_CONNECTION_STRING` environment variable or connection string parameter.

### SFTP

Requires: `pip install docu-crawler[sftp]`

```python
from docu_crawler import crawl_to_sftp

result = crawl_to_sftp(
    url="https://docs.example.com",
    host="sftp.example.com",
    user="username",
    password="password"  # or key_file="/path/to/key"
)
```

## API Reference

### DocuCrawler Class

Main crawler class for programmatic use.

```python
from docu_crawler import DocuCrawler

crawler = DocuCrawler(
    start_url: str,                    # Starting URL (required, must be HTTP/HTTPS)
    output_dir: str = "downloaded_docs", # Output directory for local storage
    delay: float = 1.0,                 # Delay between requests in seconds
    max_pages: int = 0,                 # Maximum pages to crawl (0 = unlimited)
    timeout: int = 10,                  # Request timeout in seconds
    storage_config: Optional[Dict[str, Any]] = None,  # Storage configuration dict
    single_file: bool = False           # Combine all output into one file
)
crawler.crawl()
```

**Parameters:**
- `start_url` (str): Starting URL for crawling. Must be a valid HTTP or HTTPS URL.
- `output_dir` (str): Directory where files will be saved (default: "downloaded_docs")
- `delay` (float): Delay between requests in seconds (default: 1.0, must be >= 0)
- `max_pages` (int): Maximum number of pages to crawl. 0 means unlimited (default: 0, must be >= 0)
- `timeout` (int): Request timeout in seconds (default: 10, must be > 0)
- `storage_config` (dict, optional): Storage configuration dictionary. If None, uses local storage.
- `single_file` (bool): Whether to combine all crawled content into a single `documentation.md` file (default: False)
- `on_page_crawled` (callable, optional): Callback function called when a page is successfully crawled. Signature: `(url: str, page_count: int) -> None`
- `on_error` (callable, optional): Callback function called when an error occurs. Signature: `(url: str, error: Exception) -> None`

**Raises:**
- `InvalidURLError`: If start_url is invalid
- `ValueError`: If other parameters are invalid

**Methods:**
- `crawl()`: Start the crawling process. Saves converted Markdown files to configured storage.

### Convenience Functions

All convenience functions return a dictionary with crawl results:

```python
{
    'pages_crawled': int,      # Number of pages successfully crawled
    'pages_failed': int,       # Number of pages that failed
    'urls_visited': int,       # Total number of URLs visited
    'bytes_downloaded': int,   # Total bytes downloaded
    'elapsed_time': float      # Total elapsed time in seconds
}
```

#### `crawl()`

General-purpose crawl function with full control.

```python
from docu_crawler import crawl

result = crawl(
    url: str,                              # Starting URL
    output_dir: str = "downloaded_docs",   # Output directory
    delay: float = 1.0,                    # Delay between requests
    max_pages: int = 0,                    # Max pages (0 = unlimited)
    timeout: int = 10,                     # Request timeout
    storage_config: Optional[Dict] = None,  # Storage config
    on_page_crawled: Optional[Callable] = None,  # Callback(url, page_count)
    on_error: Optional[Callable] = None    # Callback(url, error)
)
```

**Callbacks:**
- `on_page_crawled(url: str, page_count: int)`: Called when a page is successfully crawled
- `on_error(url: str, error: Exception)`: Called when an error occurs

**Note:** In v1.1.0+, callbacks are passed directly to `DocuCrawler` constructor for improved reliability and error handling.

#### `crawl_to_local()`

Crawl website and save to local filesystem.

```python
from docu_crawler import crawl_to_local

result = crawl_to_local(
    url: str,
    output_dir: str = "downloaded_docs",
    **kwargs  # Additional crawl() parameters
)
```

#### `crawl_to_s3()`

Crawl website and save to AWS S3.

```python
from docu_crawler import crawl_to_s3

result = crawl_to_s3(
    url: str,
    bucket: str,              # S3 bucket name (required)
    region: Optional[str] = None,  # AWS region
    **kwargs  # Additional crawl() parameters
)
```

**Note:** Requires `boto3`. Install with `pip install docu-crawler[s3]`

#### `crawl_to_gcs()`

Crawl website and save to Google Cloud Storage.

```python
from docu_crawler import crawl_to_gcs

result = crawl_to_gcs(
    url: str,
    bucket: str,                    # GCS bucket name (required)
    project: Optional[str] = None,  # GCP project ID
    credentials: Optional[str] = None,  # Path to credentials JSON
    **kwargs  # Additional crawl() parameters
)
```

**Note:** Requires `google-cloud-storage`. Install with `pip install docu-crawler[gcs]`

#### `crawl_to_azure()`

Crawl website and save to Azure Blob Storage.

```python
from docu_crawler import crawl_to_azure

result = crawl_to_azure(
    url: str,
    container: str,                      # Azure container name (required)
    connection_string: Optional[str] = None,  # Azure connection string
    **kwargs  # Additional crawl() parameters
)
```

**Note:** Requires `azure-storage-blob`. Install with `pip install docu-crawler[azure]`

#### `crawl_to_sftp()`

Crawl website and save via SFTP.

```python
from docu_crawler import crawl_to_sftp

result = crawl_to_sftp(
    url: str,
    host: str,                      # SFTP server hostname (required)
    user: str,                      # SFTP username (required)
    password: Optional[str] = None,  # SFTP password
    port: int = 22,                 # SFTP port
    key_file: Optional[str] = None,  # Path to SSH key file
    remote_path: str = '',          # Base remote path
    **kwargs  # Additional crawl() parameters
)
```

**Note:** Requires `paramiko`. Install with `pip install docu-crawler[sftp]`

### Exceptions

The library defines custom exceptions:

- `DocuCrawlerError`: Base exception for all docu-crawler errors
- `InvalidURLError`: Raised when an invalid URL is provided
- `ContentTooLargeError`: Raised when content exceeds maximum size limit
- `ConfigurationError`: Raised when there's a configuration error
- `StorageError`: Raised when there's a storage operation error
- `CrawlerError`: Raised when there's a crawler operation error

## Configuration

### Environment Variables

- **AWS S3**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`
- **GCS**: `GOOGLE_APPLICATION_CREDENTIALS`
- **Azure**: `AZURE_STORAGE_CONNECTION_STRING`
- **SFTP**: `SFTP_PASSWORD`, `SFTP_KEY_FILE`

### Configuration File

Create `crawler_config.yaml`:

```yaml
url: https://docs.example.com
output: downloaded_docs
delay: 1.0
max_pages: 0
timeout: 10
log_level: INFO
storage_type: s3
s3_bucket: my-bucket
s3_region: us-east-1
```

Config file locations (checked in order):
1. `./crawler_config.yaml`
2. `./config/crawler_config.yaml`
3. `~/.config/docu-crawler/config.yaml`
4. `/etc/docu-crawler/config.yaml`

## Advanced Features

### Sitemap Support

docu-crawler automatically detects and uses sitemaps if:
1. The start URL ends with `.xml` (e.g., `https://example.com/sitemap.xml`)
2. The URL contains "sitemap"

This ensures comprehensive coverage of all documentation pages.

### YAML Frontmatter

Use the `--frontmatter` flag (CLI) or `include_frontmatter=True` (Python) to add metadata to each Markdown file:

```yaml
---
title: "Page Title"
source: "https://example.com/page"
date: 2023-10-27
---
```

This is essential for RAG (Retrieval-Augmented Generation) systems and LLM indexing.

### Robots.txt Support

Automatically respects `robots.txt` files and crawl-delay directives.

### Rate Limiting

Built-in rate limiting to respect server limits. The crawler automatically uses rate limiting based on the delay parameter and robots.txt crawl-delay directives. For custom rate limiting:

```python
from docu_crawler.utils.rate_limiter import SimpleRateLimiter

limiter = SimpleRateLimiter(delay=1.0)  # 1 second delay between requests
limiter.wait_if_needed(domain="example.com")
```

### Retry Logic

Automatic retry with exponential backoff:

```python
from docu_crawler.utils.retry import retry_with_backoff

@retry_with_backoff(max_retries=3, initial_delay=1.0)
def fetch_url(url):
    pass
```

## Use Cases

### Documentation Sites
Crawl and convert documentation websites to Markdown for offline reading or migration.

### Content Migration
Migrate content from one platform to another by converting HTML to Markdown.

### Offline Documentation
Create offline versions of online documentation for local access.

### Content Analysis
Extract and analyze web content programmatically.

## Frequently Asked Questions

### How do I install docu-crawler?

```bash
pip install docu-crawler
```

For all features: `pip install docu-crawler[all]`

### What Python versions are supported?

Python 3.9 and above.

### Can I use it without cloud storage?

Yes! Local filesystem storage is the default and requires no additional dependencies.

### Does it respect robots.txt?

Yes, docu-crawler automatically respects robots.txt files and crawl-delay directives.

### Can I customize the HTML to Markdown conversion?

Yes, the HTML processor can be extended and customized for your specific needs.

### Is it fast?

docu-crawler is designed for efficiency with configurable rate limiting and retry logic.

## Troubleshooting

**Import Error**: Install docu-crawler: `pip install docu-crawler`

**Storage Backend Error**: Install the required backend: `pip install docu-crawler[s3]`

**YAML Config Error**: Install YAML support: `pip install docu-crawler[yaml]`

**SSL Certificate Error**: The crawler uses proper SSL verification by default.

**InvalidURLError**: Ensure the URL starts with `http://` or `https://`

**ContentTooLargeError**: The default maximum content size is 10MB. Large files are skipped to prevent memory issues.

**Connection Errors**: Check your network connection and ensure the target website is accessible. The crawler will retry failed requests up to 3 times.

**Encoding Errors**: v1.1.0+ includes improved encoding handling with automatic UTF-8/Latin-1 fallback for better compatibility with international sites.

**Sitemap Parsing Issues**: v1.1.0+ includes recursion protection and depth limits to prevent infinite loops when parsing nested sitemaps.

## Limitations

- **JavaScript-rendered content**: The crawler does not execute JavaScript, so content rendered dynamically by JavaScript will not be captured.
- **Authentication**: The crawler does not support authenticated sessions or login forms.
- **Rate limiting**: Always respects robots.txt and implements rate limiting, but some sites may still block aggressive crawling.
- **Large files**: Files larger than 10MB are skipped to prevent memory issues.
- **Content types**: Only HTML content is processed. Binary files, images, PDFs, etc. are skipped.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Release Process

Releases are automated via GitHub Actions. See [RELEASE.md](RELEASE.md) for details on how releases work.

## Changelog

### Version 1.1.0 (Latest)

**Bug Fixes:**
- Fixed 14+ critical bugs including NameError, IndexError, AttributeError, and KeyError issues
- Improved encoding handling for robots.txt and sitemap parsing
- Fixed type signature mismatches across storage backends
- Enhanced error handling and exception propagation

**Improvements:**
- Better callback mechanism (passed directly to constructor)
- Improved code comments and documentation
- Enhanced recursion protection for nested sitemap parsing
- Better URL validation and CLI argument handling

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **GitHub**: https://github.com/dataiscool/docu-crawler
- **Issues**: https://github.com/dataiscool/docu-crawler/issues
- **PyPI**: https://pypi.org/project/docu-crawler/

## Related Projects

- [Scrapy](https://scrapy.org/) - Full-featured web scraping framework
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing library
- [Markdownify](https://github.com/matthewwithanm/python-markdownify) - HTML to Markdown converter
