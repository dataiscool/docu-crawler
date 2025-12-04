# Changelog

## [1.0.1] - 2025-12-04

### Fixed
- Fixed LICENSE copyright placeholder (now shows correct author)
- Removed async support from setup.py and README (was advertised but not implemented)
- Fixed rate limiter example in README to match actual implementation
- Fixed code duplication in error callback handling
- Improved URL queue performance using deque instead of list
- Fixed should_add_to_queue to work with deque collections

### Added
- Comprehensive input validation for DocuCrawler initialization
- Custom exception classes (InvalidURLError, ContentTooLargeError, etc.)
- Request size limits (10MB default) to prevent memory issues
- Connection pooling using requests.Session for better performance
- Comprehensive test suite (test_doc_crawler, test_url_utils, test_storage)
- Expanded API documentation with parameter descriptions and return values
- Limitations section in README
- py.typed marker file for PEP 561 type checking support
- Constants for magic numbers (DEFAULT_STATS_LOG_INTERVAL, DEFAULT_MAX_CONTENT_LENGTH, etc.)

### Changed
- Improved error handling with custom exceptions
- Enhanced API function docstrings with complete parameter and return value documentation
- Extracted magic numbers to named constants
- Improved type hints (added Collection type for queue parameter)
- Enhanced README with detailed API reference and troubleshooting

### Security
- Added content size limits to prevent DoS attacks
- Improved path sanitization documentation

## [1.0.0] - 2025-11-23

### Changed
- Version bump to 1.0.0 - Production ready release
- Fixed file path generation to prevent nested directories
- Improved config file loading and CLI argument handling

## [0.1.2] - 2025-11-23

### Fixed
- Config file loading now works with CLI arguments
- Robots.txt checking fully integrated
- Rate limiting and retry logic properly integrated
- Error callbacks now work correctly
- Fixed elapsed_time calculation in API
- Improved import organization

### Changed
- Removed unused code and duplicate files
- Consolidated entry points

## [0.1.1] - 2025-11-23

### Added
- Multi-cloud storage support (AWS S3, Azure Blob Storage, SFTP)
- Python API with convenience functions
- Robots.txt support
- Retry logic with exponential backoff
- Rate limiting support
- Minimal dependencies (only requests and beautifulsoup4 required)

### Changed
- Refactored storage system to plugin-based architecture
- Enhanced HTML to Markdown conversion
- Updated naming to "DocuCrawler"
- Made YAML config support optional

### Fixed
- SSL verification enabled by default
- Improved cross-platform path handling

## [0.1.0] - 2025-03-17

### Added
- Initial release
- Web crawler for documentation sites
- HTML to Markdown conversion
- Local and Google Cloud Storage support
- Command-line interface

### Changed
- Python 3.9+ required
