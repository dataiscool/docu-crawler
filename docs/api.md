# Python API Reference

## DocuCrawler Class

The main class for controlling the crawl process.

```python
from docu_crawler import DocuCrawler

class DocuCrawler:
    def __init__(
        self,
        start_url: str,
        output_dir: str = "downloaded_docs",
        delay: float = 1.0,
        max_pages: int = 0,
        timeout: int = 10,
        storage_config: Optional[Dict] = None,
        single_file: bool = False,
        html_config_overrides: Optional[Dict] = None
    ): ...

    def crawl(self) -> None:
        """Start the crawling process."""
```

### Parameters

- **start_url**: The root URL to start crawling.
- **output_dir**: Local directory for saving files (default).
- **delay**: Seconds to wait between requests.
- **max_pages**: Limit total pages crawled (0 = unlimited).
- **storage_config**: Dictionary configuration for cloud storage.
- **single_file**: If `True`, combines all pages into `documentation.md`.
- **html_config_overrides**: Dictionary to configure the HTML parser (e.g., `{'include_frontmatter': True}`).

## Convenience Functions

Simple wrappers for common use cases.

```python
from docu_crawler import crawl_to_local, crawl_to_s3

# Crawl to local disk
result = crawl_to_local(
    "https://docs.example.com", 
    output_dir="docs",
    delay=2.0
)

# Crawl to S3
result = crawl_to_s3(
    "https://docs.example.com",
    bucket="my-bucket",
    frontmatter=True
)
```

## Return Values

All crawl functions return a dictionary with statistics:

```python
{
    'pages_crawled': 150,
    'pages_failed': 2,
    'urls_visited': 152,
    'bytes_downloaded': 4500000,  # bytes
    'elapsed_time': 120.5         # seconds
}
```

