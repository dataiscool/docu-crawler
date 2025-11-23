# Changelog

## [0.1.1] - 2025-11-23

### Added
- Multi-cloud storage support (AWS S3, Azure Blob Storage, SFTP)
- Python API with convenience functions
- SEO features: metadata extraction, frontmatter, sitemap generation
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
