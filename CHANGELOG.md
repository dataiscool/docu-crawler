# Changelog

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
