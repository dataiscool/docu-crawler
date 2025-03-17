# Doc Crawler

A tool for crawling documentation websites and converting them to Markdown files for offline reading.

## Features

- Crawls directories and subdirectories starting from a given URL
- Converts HTML content to Markdown format
- Preserves the site's structure in local files
- Respects robots.txt and includes configurable delays between requests
- Filters out non-documentation content and external links
- Detailed logging of the crawling process

## Installation

### From source

```bash
# Clone the repository
git clone https://github.com/dataiscool/docu-crawler.git
cd docu-crawler

# Install in development mode
pip install -e .
```

### From PyPI (once published)

```bash
pip install docu-crawler
```

## Usage

After installation, you can use the tool directly from the command line:

```bash
# Basic usage
docu-crawler https://docs.example.com

# With additional options
docu-crawler https://docs.example.com --output my-docs --delay 2 --max-pages 100
```

### Command Line Options

#### Basic Options
- `url`: The starting URL of the documentation to crawl (required unless specified in config file)
- `--output`: Directory where downloaded files will be saved (default: "downloaded_docs")
- `--delay`: Delay between requests in seconds (default: 1.0)
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--max-pages`: Maximum number of pages to download (0 for unlimited)
- `--timeout`: Request timeout in seconds (default: 10)

#### Google Cloud Storage Options
- `--use-gcs`: Store files in Google Cloud Storage instead of locally
- `--bucket`: GCS bucket name (required if --use-gcs is specified)
- `--project`: Google Cloud project ID (optional, uses project from credentials if not specified)
- `--credentials`: Path to Google Cloud credentials JSON file

#### Configuration Options
- `--config`: Path to configuration file

## Examples

```bash
# Basic crawl of Python documentation
docu-crawler https://docs.python.org/3/ --output python-docs --delay 1.5

# Crawl with debug logs for more detail
docu-crawler https://docs.python.org/3/library/ --output python-lib --log-level DEBUG

# Crawl with longer timeout for slow servers
docu-crawler https://docs.example.com --timeout 30

# Crawl only a limited number of pages
docu-crawler https://cloud.google.com/run/docs/ --output cloud_run --max-pages 50

# Store files in Google Cloud Storage
docu-crawler https://docs.example.com --use-gcs --bucket my-docs-bucket

# Specify GCS credentials explicitly
docu-crawler https://docs.example.com --use-gcs --bucket my-docs-bucket --credentials ./gcp-credentials.json

# Specify GCP project ID explicitly
docu-crawler https://docs.example.com --use-gcs --bucket my-docs-bucket --project my-gcp-project

# Run without arguments (loads from config file)
docu-crawler
```

## Configuration File

You can configure the crawler using a YAML file instead of command-line arguments. The crawler will look for a configuration file in the following locations:

1. `./crawler_config.yaml` (current directory)
2. `./config/crawler_config.yaml`
3. `~/.config/doc-crawler/config.yaml`
4. `/etc/doc-crawler/config.yaml`

You can also specify a custom path with the `--config` option.

Example configuration file:

```yaml
# Target URL to crawl
url: https://docs.example.com

# Output settings
output: downloaded_docs

# Crawler behavior
delay: 1.0
max_pages: 0  # 0 for unlimited
timeout: 10
log_level: INFO

# Google Cloud Storage settings
use_gcs: true
bucket: my-docs-bucket
project: my-gcp-project-id  # Optional
credentials: /path/to/credentials.json
```

## Google Cloud Storage

To store downloaded files in Google Cloud Storage:

1. **Authentication**: The crawler can authenticate with Google Cloud in the following ways:
   - Using a service account key file (JSON) specified with `--credentials`
   - Using the `GOOGLE_APPLICATION_CREDENTIALS` environment variable
   - Checking for credentials in common locations (`./credentials.json`, `./config/credentials.json`, etc.)
   - Using application default credentials if the above methods fail

2. **Project Selection**:
   - By default, the project is determined by the credentials being used
   - You can explicitly specify a project with the `--project` option
   - The project ID is used for bucket creation and access

3. **Required Options**:
   - `--use-gcs`: Enable Google Cloud Storage output
   - `--bucket`: Specify the GCS bucket name

4. **Bucket Creation**: If the bucket doesn't exist, the crawler will attempt to create it in the specified project.

## Project Structure

```
doc-crawler/
├── src/                  # Source code package
│   ├── models/           # Data models
│   │   └── crawler_stats.py
│   ├── processors/       # Content processors
│   │   └── html_processor.py
│   ├── utils/            # Utility functions
│   │   ├── cli.py        # CLI argument parsing
│   │   ├── config.py     # Configuration loading
│   │   ├── logger.py     # Logging setup
│   │   ├── storage.py    # Storage abstraction (local/GCS)
│   │   └── url_utils.py  # URL operations
│   ├── cli.py            # CLI entry point
│   └── doc_crawler.py    # Main crawler class
├── crawler_config.yaml.example  # Example configuration file
├── setup.py              # Package setup file
└── README.md             # Project documentation
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
