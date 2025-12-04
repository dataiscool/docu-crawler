import argparse
import logging
from typing import Tuple, Any

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for the crawler.
    
    Returns:
        Namespace containing the parsed arguments
    """
    parser = argparse.ArgumentParser(description='Docu Crawler - Web Crawler Library')
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
    parser.add_argument('--single-file', action='store_true',
                        help='Combine all crawled pages into a single Markdown file (default: False)')
    parser.add_argument('--frontmatter', action='store_true',
                        help='Add YAML frontmatter to Markdown files (default: False)')
    
    storage_group = parser.add_argument_group('Storage options')
    storage_group.add_argument('--storage-type', 
                              choices=['local', 'gcs', 's3', 'azure', 'sftp'],
                              default='local',
                              help='Storage backend type (default: local)')
    
    gcs_group = parser.add_argument_group('Google Cloud Storage options')
    gcs_group.add_argument('--use-gcs', action='store_true',
                           help='Store files in Google Cloud Storage (deprecated: use --storage-type gcs)')
    gcs_group.add_argument('--bucket', 
                           help='GCS bucket name (required if using GCS)')
    gcs_group.add_argument('--project', 
                           help='Google Cloud project ID (if not specified, uses the project from credentials)')
    gcs_group.add_argument('--credentials', 
                           help='Path to Google Cloud credentials JSON file')
    
    s3_group = parser.add_argument_group('AWS S3 Storage options')
    s3_group.add_argument('--s3-bucket', 
                          help='S3 bucket name (required if --storage-type s3)')
    s3_group.add_argument('--s3-region', 
                          help='AWS region (e.g., us-east-1, default: from AWS_DEFAULT_REGION env)')
    s3_group.add_argument('--s3-endpoint-url',
                          help='Custom S3 endpoint URL (for S3-compatible services)')
    
    azure_group = parser.add_argument_group('Azure Blob Storage options')
    azure_group.add_argument('--azure-container',
                             help='Azure container name (required if --storage-type azure)')
    azure_group.add_argument('--azure-connection-string',
                             help='Azure storage connection string')
    
    sftp_group = parser.add_argument_group('SFTP Storage options')
    sftp_group.add_argument('--sftp-host',
                            help='SFTP server hostname (required if --storage-type sftp)')
    sftp_group.add_argument('--sftp-user',
                            help='SFTP username (required if --storage-type sftp)')
    sftp_group.add_argument('--sftp-password',
                            help='SFTP password (optional if using key file)')
    sftp_group.add_argument('--sftp-port', type=int, default=22,
                            help='SFTP port (default: 22)')
    sftp_group.add_argument('--sftp-key-file',
                            help='Path to SSH private key file')
    sftp_group.add_argument('--sftp-remote-path',
                            help='Base remote path for SFTP storage')
    
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
