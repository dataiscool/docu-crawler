# Configuration

DocuCrawler can be configured via a YAML file, command-line arguments, or environment variables.

## Configuration File

You can create a `crawler_config.yaml` file in your project root.

```yaml
# Target URL
url: https://docs.example.com

# Output directory
output: downloaded_docs

# Crawling behavior
delay: 1.0          # Seconds between requests
max_pages: 0        # 0 = unlimited
timeout: 10         # Request timeout in seconds
log_level: INFO     # DEBUG, INFO, WARNING, ERROR

# Features
single_file: false  # Combine into one file
frontmatter: false  # Add YAML frontmatter

# Storage (default: local)
storage_type: local
```

Load it with:
```bash
docu-crawler --config crawler_config.yaml
```

## Command Line Arguments

CLI arguments override configuration file settings.

| Argument | Description | Default |
|----------|-------------|---------|
| `url` | The starting URL (positional argument) | None |
| `--output` | Output directory | `downloaded_docs` |
| `--delay` | Delay between requests in seconds | `1.0` |
| `--max-pages` | Maximum pages to crawl (0=unlimited) | `0` |
| `--timeout` | Request timeout in seconds | `10` |
| `--single-file` | Combine output into one Markdown file | `False` |
| `--frontmatter` | Add YAML frontmatter to files | `False` |
| `--log-level` | Logging verbosity | `INFO` |
| `--storage-type` | Backend: local, s3, gcs, azure, sftp | `local` |

## Environment Variables

Secure credentials should be passed via environment variables.

### General
- `DOCU_CRAWLER_CONFIG`: Path to config file

### AWS S3
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`

### Google Cloud Storage
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account JSON

### Azure Blob Storage
- `AZURE_STORAGE_CONNECTION_STRING`

### SFTP
- `SFTP_PASSWORD`
- `SFTP_KEY_FILE`

