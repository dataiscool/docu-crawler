from urllib.parse import urlparse
import logging
from typing import Set

logger = logging.getLogger('DocCrawler')

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
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Check if the URL is from the same domain
    if parsed_url.netloc != base_domain:
        logger.debug(f"Skipping external domain: {url}")
        return False
    
    # Check if the URL is within the documentation path
    if not parsed_url.path.startswith(base_path):
        logger.debug(f"Skipping outside base path: {url}")
        return False
    
    # Filter out non-HTML content
    extensions_to_avoid = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.js', '.css']
    if any(parsed_url.path.endswith(ext) for ext in extensions_to_avoid):
        logger.debug(f"Skipping non-HTML file: {url}")
        return False
        
    return True

def url_to_filepath(url: str, base_path: str, output_dir: str) -> str:
    """
    Convert a URL to a local file path.
    
    Args:
        url: The URL to convert
        base_path: The base path to remove from the URL path
        output_dir: Directory where the file should be saved
        
    Returns:
        The local file path
    """
    import os
    parsed_url = urlparse(url)
    
    # Extract the path and remove the initial part matching base_path
    path = parsed_url.path
    if path.startswith(base_path):
        path = path[len(base_path):]
    
    # Handle index pages
    if path.endswith('/'):
        path = path + 'index'
    
    # Remove the initial slash if it exists
    if path.startswith('/'):
        path = path[1:]
    
    # Create a file name based on the path
    file_path = os.path.join(output_dir, path)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Add .md extension for Markdown files
    if not file_path.endswith('.md'):
        file_path += '.md'
        
    return file_path

def should_add_to_queue(url: str, visited_urls: Set[str], urls_to_visit: list) -> bool:
    """
    Determine if a URL should be added to the crawl queue.
    
    Args:
        url: The URL to check
        visited_urls: Set of already visited URLs
        urls_to_visit: List of URLs to visit
        
    Returns:
        True if the URL should be added to the queue, False otherwise
    """
    return url not in visited_urls and url not in urls_to_visit
