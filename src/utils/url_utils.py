import os
from urllib.parse import urlparse
import logging
from typing import Set, Union, Collection

logger = logging.getLogger('DocuCrawler')

NON_HTML_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.js', '.css', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot']

def is_valid_url(url: str, base_domain: str, base_path: str) -> bool:
    """
    Check if the URL is valid and belongs to the documentation.
    
    Args:
        url: URL to check
        base_domain: The base domain to validate against
        base_path: The base path to validate against
        
    Returns:
        True if the URL is valid, False otherwise
    """
    parsed_url = urlparse(url)
    
    if parsed_url.netloc != base_domain:
        logger.debug(f"Skipping external domain: {url}")
        return False
    
    if not parsed_url.path.startswith(base_path):
        logger.debug(f"Skipping outside base path: {url}")
        return False
    
    if any(parsed_url.path.lower().endswith(ext) for ext in NON_HTML_EXTENSIONS):
        logger.debug(f"Skipping non-HTML file: {url}")
        return False
        
    return True

def url_to_filepath(url: str, base_path: str, output_dir: str) -> str:
    """
    Convert a URL to a relative file path (without output_dir).
    
    Args:
        url: The URL to convert
        base_path: The base path to remove from the URL path
        output_dir: Directory where the file should be saved (for reference only)
    
    Returns:
        Relative file path (without output_dir prefix)
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    if path.startswith(base_path):
        path = path[len(base_path):]
    
    if path.endswith('/'):
        path = path + 'index'
    
    if path.startswith('/'):
        path = path[1:]
    
    if not path or path == '':
        path = 'index'
    
    if not path.endswith('.md'):
        path += '.md'
    
    return path

def should_add_to_queue(url: str, visited_urls: Set[str], urls_in_queue: Set[str]) -> bool:
    """
    Determine if a URL should be added to the crawl queue.
    
    Args:
        url: The URL to check
        visited_urls: Set of already visited URLs
        urls_in_queue: Set of URLs already in the queue (for O(1) lookup)
        
    Returns:
        True if the URL should be added to the queue, False otherwise
    """
    return url not in visited_urls and url not in urls_in_queue
