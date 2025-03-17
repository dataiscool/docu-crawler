import argparse
import logging
from typing import Tuple, Any

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for the crawler.
    
    Returns:
        Namespace containing the parsed arguments
    """
    parser = argparse.ArgumentParser(description='Documentation Web Crawler')
    parser.add_argument('url', nargs='?', help='The starting URL of the documentation')
    parser.add_argument('--output', help='Output directory for downloaded files (default: downloaded_docs)')
    parser.add_argument('--delay', type=float, help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--log-level', 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level (default: INFO)')
    parser.add_argument('--max-pages', type=int, 
                        help='Maximum number of pages to download (0 for unlimited, default: 0)')
    parser.add_argument('--timeout', type=int,
                        help='Request timeout in seconds (default: 10)')
    
    # GCS options
    gcs_group = parser.add_argument_group('Google Cloud Storage options')
    gcs_group.add_argument('--use-gcs', action='store_true',
                           help='Store files in Google Cloud Storage instead of locally')
    gcs_group.add_argument('--bucket', 
                           help='GCS bucket name (required if --use-gcs is specified)')
    gcs_group.add_argument('--project', 
                           help='Google Cloud project ID (if not specified, uses the project from credentials)')
    gcs_group.add_argument('--credentials', 
                           help='Path to Google Cloud credentials JSON file')
    
    # Config file options
    config_group = parser.add_argument_group('Configuration options')
    config_group.add_argument('--config', 
                              help='Path to configuration file (default: searches in standard locations)')
    
    return parser.parse_args()

def get_log_level(level_name: str) -> int:
    """
    Convert a string log level to the corresponding logging level.
    
    Args:
        level_name: String representation of the log level
        
    Returns:
        The corresponding logging level constant
    """
    return getattr(logging, level_name)
