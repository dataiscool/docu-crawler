#!/usr/bin/env python3

"""
Documentation Web Crawler

This script is the entry point for the documentation crawler application.
It crawls documentation websites and saves them as Markdown files for offline reading.
"""

import sys
import os

from src.utils.logger import setup_logger
from src.utils.cli import parse_args, get_log_level
from src.doc_crawler import DocCrawler

def main():
    """
    Main function to run the documentation crawler.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Set up logging
    logger = setup_logger(log_level=get_log_level(args.log_level))
    
    try:
        # Create and run the crawler
        crawler = DocCrawler(
            args.url, 
            args.output, 
            args.delay,
            args.max_pages,
            args.timeout
        )
        crawler.crawl()
    except KeyboardInterrupt:
        logger.info("Crawler stopped by user")
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
