#!/usr/bin/env python3

import sys
import os

from src.utils.logger import setup_logger
from src.utils.cli import parse_args, get_log_level
from src.doc_crawler import DocuCrawler

def main():
    """Main function to run the docu-crawler."""
    args = parse_args()
    logger = setup_logger(log_level=get_log_level(args.log_level))
    
    try:
        crawler = DocuCrawler(
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
