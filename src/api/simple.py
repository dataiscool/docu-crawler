"""
Simple API functions for common crawling tasks.

This module re-exports the main API functions for convenience.
"""

from . import (
    crawl,
    crawl_to_local,
    crawl_to_s3,
    crawl_to_gcs,
    crawl_to_azure,
    crawl_to_sftp,
    DocuCrawler,
    WebCrawler,
    DocCrawler
)

__all__ = [
    'crawl',
    'crawl_to_local',
    'crawl_to_s3',
    'crawl_to_gcs',
    'crawl_to_azure',
    'crawl_to_sftp',
    'DocuCrawler',
    'WebCrawler',
    'DocCrawler'
]

