"""
Custom exceptions for docu-crawler.
"""

class DocuCrawlerError(Exception):
    """Base exception for all docu-crawler errors."""
    pass

class ConfigurationError(DocuCrawlerError):
    """Raised when there's a configuration error."""
    pass

class StorageError(DocuCrawlerError):
    """Raised when there's a storage operation error."""
    pass

class CrawlerError(DocuCrawlerError):
    """Raised when there's a crawler operation error."""
    pass

class ContentTooLargeError(CrawlerError):
    """Raised when content exceeds maximum size limit."""
    pass

class InvalidURLError(CrawlerError):
    """Raised when an invalid URL is provided."""
    pass

