"""
docu-crawler - A lightweight web crawler library for HTML to Markdown conversion.

Main exports:
    - DocuCrawler: Main crawler class
    - crawl: Convenience function for crawling
    - crawl_to_local, crawl_to_s3, crawl_to_gcs, etc.: Storage-specific functions
"""

__version__ = '1.1.0'

from .doc_crawler import DocuCrawler
DocCrawler = DocuCrawler
WebCrawler = DocuCrawler

from .api import (
    crawl,
    crawl_to_local,
    crawl_to_s3,
    crawl_to_gcs,
    crawl_to_azure,
    crawl_to_sftp
)

from .exceptions import (
    DocuCrawlerError,
    ConfigurationError,
    StorageError,
    CrawlerError,
    ContentTooLargeError,
    InvalidURLError
)

__all__ = [
    'DocuCrawler', 
    'DocCrawler', 
    'WebCrawler', 
    '__version__',
    'crawl',
    'crawl_to_local',
    'crawl_to_s3',
    'crawl_to_gcs',
    'crawl_to_azure',
    'crawl_to_sftp',
    'DocuCrawlerError',
    'ConfigurationError',
    'StorageError',
    'CrawlerError',
    'ContentTooLargeError',
    'InvalidURLError'
]
