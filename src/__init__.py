"""
docu-crawler - A lightweight web crawler library for HTML to Markdown conversion.

Main exports:
    - DocuCrawler: Main crawler class
    - crawl: Convenience function for crawling
    - crawl_to_local, crawl_to_s3, crawl_to_gcs, etc.: Storage-specific functions
"""

__version__ = '0.1.1'

# Backward compatibility aliases
from .doc_crawler import DocuCrawler
DocCrawler = DocuCrawler
WebCrawler = DocuCrawler

__all__ = ['DocuCrawler', 'DocCrawler', 'WebCrawler', '__version__']
