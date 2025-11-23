#!/usr/bin/env python3

import sys
import os
import logging
from typing import Dict, Any
import argparse

from src.utils.logger import setup_logger
from src.utils.cli import parse_args, get_log_level
from src.utils.config import load_config, merge_config_and_args, get_credentials_path, get_storage_config
from src.doc_crawler import DocuCrawler

WebCrawler = DocuCrawler
DocCrawler = DocuCrawler

DEFAULTS = {
    'url': None,
    'output': 'downloaded_docs',
    'delay': 1.0,
    'log_level': 'INFO',
    'max_pages': 0,
    'timeout': 10,
    'storage_type': 'local',
    'use_gcs': False,
    'bucket': None,
    'project': None,
    'credentials': None
}

def args_to_dict(args: argparse.Namespace) -> Dict[str, Any]:
    """Convert argparse namespace to a dictionary."""
    return {k: v for k, v in vars(args).items() if k != 'config'}

def run():
    """Main function to run the docu crawler from CLI."""
    args = parse_args()
    
    config = {}
    if not args.url:
        config = load_config()
        if not config.get('url'):
            print("Error: No URL specified and no URL found in config file.")
            print("Please provide a URL as an argument or in a config file.")
            return 1
    
    args_dict = args_to_dict(args)
    
    if args_dict.get('use_gcs'):
        args_dict['storage_type'] = 'gcs'
    
    params = merge_config_and_args(config, args_dict)
    
    for key, value in DEFAULTS.items():
        if params.get(key) is None:
            params[key] = value
    
    storage_type = params.get('storage_type', 'local')
    if storage_type == 'gcs' and not params.get('bucket'):
        print("Error: When using GCS storage, a bucket name (--bucket) is required.")
        return 1
    elif storage_type == 's3' and not params.get('s3_bucket'):
        print("Error: When using S3 storage, a bucket name (--s3-bucket) is required.")
        return 1
    elif storage_type == 'azure' and not params.get('azure_container'):
        print("Error: When using Azure storage, a container name (--azure-container) is required.")
        return 1
    elif storage_type == 'sftp':
        if not params.get('sftp_host') or not params.get('sftp_user'):
            print("Error: When using SFTP storage, --sftp-host and --sftp-user are required.")
            return 1
    
    if storage_type == 'gcs' and not params.get('credentials'):
        params['credentials'] = get_credentials_path()
    
    logger = setup_logger(log_level=get_log_level(params['log_level']))
    
    try:
        logger.info("Starting crawler with the following configuration:")
        for key, value in params.items():
            if key in ['credentials', 'sftp_password', 'aws_secret_access_key', 'azure_account_key']:
                if value:
                    logger.info(f"  {key}: [provided]")
            else:
                logger.info(f"  {key}: {value}")
        
        storage_config = get_storage_config(params)
        
        crawler = DocuCrawler(
            start_url=params['url'], 
            output_dir=params.get('output', 'downloaded_docs'), 
            delay=params['delay'],
            max_pages=params['max_pages'],
            timeout=params['timeout'],
            storage_config=storage_config
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
