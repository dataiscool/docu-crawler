# Crawling Features

DocuCrawler includes several built-in features to ensure robust and polite crawling.

## Robots.txt Respect

The crawler automatically checks the `robots.txt` file of the target domain.
- It respects `User-agent: *` rules.
- It respects `Disallow` paths.
- It respects the `Crawl-delay` directive (automatically adjusting the delay).

No configuration is needed; this is enabled by default.

## Sitemap Support

Instead of discovering links solely by crawling (which might miss orphaned pages), DocuCrawler can use the site's `sitemap.xml`.

**Automatic Detection**:
If your start URL ends in `.xml` or contains `sitemap` (e.g., `https://example.com/sitemap.xml`), the crawler automatically switches to sitemap mode.

1. It fetches the sitemap.
2. Parses all URLs (including nested sitemaps).
3. Adds valid URLs (matching the domain) to the crawl queue.

**Usage**:
```bash
docu-crawler https://docs.example.com/sitemap.xml
```

## Rate Limiting

To avoid overwhelming servers, you can configure a delay between requests.

- **Default**: 1.0 second
- **Configuration**: `--delay 2.0` or `delay: 2.0` in config.

If `robots.txt` specifies a longer `Crawl-delay`, the crawler will honor the longer delay automatically.

## Retry Logic

Network requests can fail. DocuCrawler implements exponential backoff retry logic.

- **Retries**: 3 attempts by default.
- **Backoff**: Waiting time doubles after each failure (1s, 2s, 4s).
- **Errors**: Handles common HTTP errors (5xx, 429) and network timeouts.

## Request Validation

- **Domain Locking**: The crawler stays within the subdomain of the start URL.
- **Path Locking**: The crawler stays within the path of the start URL (e.g., if starting at `/docs/v1/`, it won't crawl `/docs/v2/`).
- **File Types**: Non-HTML files (images, PDFs, zips) are automatically skipped to save bandwidth.
- **Size Limit**: Responses larger than 10MB are skipped to prevent memory exhaustion.

