# docu-crawler: Python Web Crawler for HTML to Markdown Conversion

> **Fast, lightweight Python library for crawling websites and converting HTML to Markdown. Perfect for documentation extraction, content migration, and offline reading.**

**docu-crawler** is a production-ready Python web crawler that extracts, converts, and stores web content efficiently. Crawl documentation sites, migrate content, and create offline documentation with minimal dependencies.

## What is docu-crawler?

**docu-crawler** is a specialized Python web crawler library designed for:

- **Web Crawling**: Systematically crawl websites while respecting robots.txt
- **HTML to Markdown Conversion**: Convert HTML pages to clean, readable Markdown format
- **Content Extraction**: Extract and preserve website structure and content
- **Multi-Cloud Storage**: Store crawled content locally or in cloud storage (AWS S3, Google Cloud Storage, Azure Blob Storage, SFTP)

## Why Choose docu-crawler?

- ✅ **Minimal Dependencies**: Only requires `requests` and `beautifulsoup4` for core functionality
- ✅ **Easy to Use**: Simple Python API and CLI interface
- ✅ **Production Ready**: Built-in retry logic, rate limiting, and error handling
- ✅ **Extensible**: Plugin-based storage system, easy to add custom backends
- ✅ **Cross-Platform**: Works on Linux, Windows, and macOS

## Key Features

- 🚀 **Lightweight**: Minimal dependencies (only `requests` and `beautifulsoup4` required)
- ☁️ **Multi-Cloud Storage**: Support for local filesystem, AWS S3, Google Cloud Storage, Azure Blob Storage, and SFTP
- 🔄 **Flexible API**: Use as a Python library or CLI tool
- 📝 **HTML to Markdown**: Intelligent conversion preserving structure and formatting
- 🤖 **Robots.txt Support**: Respects robots.txt and crawl-delay directives
- ⚡ **Performance**: Configurable rate limiting and retry logic
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
pip install docu-crawler[yaml]      # YAML config file support
pip install docu-crawler[s3]        # AWS S3 storage
pip install docu-crawler[gcs]       # Google Cloud Storage
pip install docu-crawler[azure]     # Azure Blob Storage
pip install docu-crawler[sftp]      # SFTP storage
pip install docu-crawler[async]      # Async support
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
docu-crawler https://docs.example.com --output my-docs --delay 2 --max-pages 100
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

- `crawl(url, output_dir, delay, max_pages, timeout, storage_config, on_page_crawled, on_error)` - General-purpose crawl function
- `crawl_to_local(url, output_dir, **kwargs)` - Crawl to local filesystem
- `crawl_to_s3(url, bucket, region=None, **kwargs)` - Crawl to AWS S3
- `crawl_to_gcs(url, bucket, project=None, credentials=None, **kwargs)` - Crawl to Google Cloud Storage
- `crawl_to_azure(url, container, connection_string=None, **kwargs)` - Crawl to Azure Blob Storage
- `crawl_to_sftp(url, host, user, password=None, port=22, key_file=None, remote_path='', **kwargs)` - Crawl via SFTP

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

### Robots.txt Support

Automatically respects `robots.txt` files and crawl-delay directives.

### Rate Limiting

Built-in rate limiting to respect server limits:

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

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

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
