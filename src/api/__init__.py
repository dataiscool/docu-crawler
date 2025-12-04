import time
from typing import Optional, Dict, Any, Callable
from src.doc_crawler import DocuCrawler

WebCrawler = DocuCrawler
DocCrawler = DocuCrawler

__all__ = ['crawl', 'crawl_to_local', 'crawl_to_s3', 'crawl_to_gcs', 'crawl_to_azure', 'crawl_to_sftp', 'DocuCrawler', 'WebCrawler', 'DocCrawler']

def crawl(url: str, 
          output_dir: str = "downloaded_docs",
          delay: float = 1.0,
          max_pages: int = 0,
          timeout: int = 10,
          storage_config: Optional[Dict[str, Any]] = None,
          on_page_crawled: Optional[Callable[[str, int], None]] = None,
          on_error: Optional[Callable[[str, Exception], None]] = None) -> Dict[str, Any]:
    """
    Crawl a website and convert HTML pages to Markdown.
    
    Args:
        url: Starting URL for crawling (must be valid HTTP/HTTPS URL)
        output_dir: Directory where files will be saved (default: "downloaded_docs")
        delay: Delay between requests in seconds (default: 1.0)
        max_pages: Maximum number of pages to crawl, 0 for unlimited (default: 0)
        timeout: Request timeout in seconds (default: 10)
        storage_config: Storage configuration dictionary (default: None, uses local storage)
        on_page_crawled: Optional callback function called when a page is successfully crawled.
                        Receives (url: str, page_count: int) as arguments.
        on_error: Optional callback function called when an error occurs.
                  Receives (url: str, error: Exception) as arguments.
    
    Returns:
        Dictionary with crawl results containing:
        - pages_crawled (int): Number of pages successfully crawled
        - pages_failed (int): Number of pages that failed
        - urls_visited (int): Total number of URLs visited
        - bytes_downloaded (int): Total bytes downloaded
        - elapsed_time (float): Total elapsed time in seconds
    
    Raises:
        InvalidURLError: If URL is invalid
        ValueError: If other parameters are invalid
        ContentTooLargeError: If content exceeds maximum size limit
    
    Example:
        >>> result = crawl("https://docs.example.com", output_dir="my_docs")
        >>> print(f"Crawled {result['pages_crawled']} pages")
    """
    crawler = DocuCrawler(
        start_url=url,
        output_dir=output_dir,
        delay=delay,
        max_pages=max_pages,
        timeout=timeout,
        storage_config=storage_config,
        on_page_crawled=on_page_crawled,
        on_error=on_error
    )
    
    crawler.crawl()
    
    elapsed_time = time.time() - crawler.stats.start_time
    
    return {
        'pages_crawled': crawler.stats.pages_processed,
        'pages_failed': crawler.stats.pages_failed,
        'urls_visited': len(crawler.visited_urls),
        'bytes_downloaded': crawler.stats.bytes_downloaded,
        'elapsed_time': elapsed_time
    }

def crawl_to_local(url: str, output_dir: str = "downloaded_docs", **kwargs) -> Dict[str, Any]:
    """
    Crawl website and save to local filesystem.
    
    Args:
        url: Starting URL for crawling
        output_dir: Directory where files will be saved
        **kwargs: Additional arguments passed to crawl() function
    
    Returns:
        Dictionary with crawl results (see crawl() for details)
    """
    return crawl(url, output_dir=output_dir, storage_config={'storage_type': 'local', 'output': output_dir}, **kwargs)

def crawl_to_s3(url: str, bucket: str, region: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Crawl website and save to AWS S3.
    
    Args:
        url: Starting URL for crawling
        bucket: S3 bucket name (required)
        region: AWS region (optional, uses AWS_DEFAULT_REGION env var if not provided)
        **kwargs: Additional arguments passed to crawl() function
    
    Returns:
        Dictionary with crawl results (see crawl() for details)
    
    Note:
        Requires boto3. Install with: pip install docu-crawler[s3]
        Credentials via AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY env vars or AWS credentials file.
    """
    storage_config = {
        'storage_type': 's3',
        's3_bucket': bucket,
        's3_region': region
    }
    return crawl(url, storage_config=storage_config, **kwargs)

def crawl_to_gcs(url: str, bucket: str, project: Optional[str] = None, credentials: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Crawl website and save to Google Cloud Storage.
    
    Args:
        url: Starting URL for crawling
        bucket: GCS bucket name (required)
        project: GCP project ID (optional, uses project from credentials if not provided)
        credentials: Path to credentials JSON file (optional, uses GOOGLE_APPLICATION_CREDENTIALS env var if not provided)
        **kwargs: Additional arguments passed to crawl() function
    
    Returns:
        Dictionary with crawl results (see crawl() for details)
    
    Note:
        Requires google-cloud-storage. Install with: pip install docu-crawler[gcs]
    """
    storage_config = {
        'storage_type': 'gcs',
        'bucket': bucket,
        'project': project,
        'credentials': credentials
    }
    return crawl(url, storage_config=storage_config, **kwargs)

def crawl_to_azure(url: str, container: str, connection_string: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Crawl website and save to Azure Blob Storage.
    
    Args:
        url: Starting URL for crawling
        container: Azure container name (required)
        connection_string: Azure storage connection string (optional, uses AZURE_STORAGE_CONNECTION_STRING env var if not provided)
        **kwargs: Additional arguments passed to crawl() function
    
    Returns:
        Dictionary with crawl results (see crawl() for details)
    
    Note:
        Requires azure-storage-blob. Install with: pip install docu-crawler[azure]
    """
    storage_config = {
        'storage_type': 'azure',
        'azure_container': container,
        'azure_connection_string': connection_string
    }
    return crawl(url, storage_config=storage_config, **kwargs)

def crawl_to_sftp(url: str, host: str, user: str, password: Optional[str] = None, 
                  port: int = 22, key_file: Optional[str] = None, remote_path: str = '', **kwargs) -> Dict[str, Any]:
    """
    Crawl website and save via SFTP.
    
    Args:
        url: Starting URL for crawling
        host: SFTP server hostname (required)
        user: SFTP username (required)
        password: SFTP password (optional if using key_file)
        port: SFTP port (default: 22)
        key_file: Path to SSH private key file (optional, uses SFTP_KEY_FILE env var if not provided)
        remote_path: Base remote path for SFTP storage (default: '')
        **kwargs: Additional arguments passed to crawl() function
    
    Returns:
        Dictionary with crawl results (see crawl() for details)
    
    Note:
        Requires paramiko. Install with: pip install docu-crawler[sftp]
    """
    storage_config = {
        'storage_type': 'sftp',
        'sftp_host': host,
        'sftp_user': user,
        'sftp_password': password,
        'sftp_port': port,
        'sftp_key_file': key_file,
        'sftp_remote_path': remote_path
    }
    return crawl(url, storage_config=storage_config, **kwargs)
