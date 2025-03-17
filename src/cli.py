#!/usr/bin/env python3

"""
Documentation Web Crawler CLI

This module provides the command-line interface for the crawler.
"""

import sys
import os
import logging
from typing import Dict, Any
import argparse

from src.utils.logger import setup_logger
from src.utils.cli import parse_args, get_log_level
from src.utils.config import load_config, merge_config_and_args, get_credentials_path
from src.doc_crawler import DocCrawler

# Default values
DEFAULTS = {
    'url': None,
    'output': 'downloaded_docs',
    'delay': 1.0,
    'log_level': 'INFO',
    'max_pages': 0,
    'timeout': 10,
    'use_gcs': False,
    'bucket': None,
    'project': None,
    'credentials': None
}

def args_to_dict(args: argparse.Namespace) -> Dict[str, Any]:
    """Convert argparse namespace to a dictionary."""
    return {k: v for k, v in vars(args).items() if k != 'config'}

def run():
    """
    Main function to run the documentation crawler from CLI.
    This is the entry point for the console_script.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Check if we need to load config from file
    config = {}
    if not args.url:  # No URL provided - check config
        config = load_config()
        if not config.get('url'):
            print("Error: No URL specified and no URL found in config file.")
            print("Please provide a URL as an argument or in a config file.")
            return 1
    
    # Convert args to dict for merging with config
    args_dict = args_to_dict(args)
    
    # Merge config and args (args take precedence)
    params = merge_config_and_args(config, args_dict)
    
    # Apply defaults for missing parameters
    for key, value in DEFAULTS.items():
        if params.get(key) is None:
            params[key] = value
    
    # If use_gcs is True but no bucket specified, show error
    if params['use_gcs'] and not params['bucket']:
        print("Error: When using GCS storage (--use-gcs), a bucket name (--bucket) is required.")
        return 1
    
    # If no credentials path specified, try to find one
    if params['use_gcs'] and not params['credentials']:
        params['credentials'] = get_credentials_path()
    
    # Set up logging
    logger = setup_logger(log_level=get_log_level(params['log_level']))
    
    try:
        # Show effective configuration
        logger.info("Starting crawler with the following configuration:")
        for key, value in params.items():
            if key == 'credentials' and value:
                # Don't log the full credentials path
                logger.info(f"  {key}: [credentials file provided]")
            else:
                logger.info(f"  {key}: {value}")
        
        # Create and run the crawler
        crawler = DocCrawler(
            start_url=params['url'], 
            output_dir=params['output'], 
            delay=params['delay'],
            max_pages=params['max_pages'],
            timeout=params['timeout'],
            use_gcs=params['use_gcs'],
            bucket_name=params['bucket'],
            project_id=params['project'],
            credentials_path=params['credentials']
        )
        crawler.crawl()
    except KeyboardInterrupt:
        logger.info("Crawler stopped by user")
        return 1
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(run())