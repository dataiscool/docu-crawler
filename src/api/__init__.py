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
    """Crawl a website and return results."""
    crawler = DocuCrawler(
        start_url=url,
        output_dir=output_dir,
        delay=delay,
        max_pages=max_pages,
        timeout=timeout,
        storage_config=storage_config
    )
    
    if on_page_crawled:
        original_process = crawler.process_page
        def process_with_callback(url, response):
            result = original_process(url, response)
            if result:
                on_page_crawled(url, crawler.stats.pages_processed)
            return result
        crawler.process_page = process_with_callback
    
    if on_error:
        crawler._on_error_callback = on_error
    
    crawler.crawl()
    
    return {
        'pages_crawled': crawler.stats.pages_processed,
        'pages_failed': crawler.stats.pages_failed,
        'urls_visited': len(crawler.visited_urls),
        'bytes_downloaded': crawler.stats.bytes_downloaded,
        'elapsed_time': crawler.stats.start_time
    }

def crawl_to_local(url: str, output_dir: str = "downloaded_docs", **kwargs) -> Dict[str, Any]:
    """Crawl website to local filesystem."""
    return crawl(url, output_dir=output_dir, storage_config={'storage_type': 'local', 'output': output_dir}, **kwargs)

def crawl_to_s3(url: str, bucket: str, region: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Crawl website to AWS S3."""
    storage_config = {
        'storage_type': 's3',
        's3_bucket': bucket,
        's3_region': region
    }
    return crawl(url, storage_config=storage_config, **kwargs)

def crawl_to_gcs(url: str, bucket: str, project: Optional[str] = None, credentials: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Crawl website to Google Cloud Storage."""
    storage_config = {
        'storage_type': 'gcs',
        'bucket': bucket,
        'project': project,
        'credentials': credentials
    }
    return crawl(url, storage_config=storage_config, **kwargs)

def crawl_to_azure(url: str, container: str, connection_string: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Crawl website to Azure Blob Storage."""
    storage_config = {
        'storage_type': 'azure',
        'azure_container': container,
        'azure_connection_string': connection_string
    }
    return crawl(url, storage_config=storage_config, **kwargs)

def crawl_to_sftp(url: str, host: str, user: str, password: Optional[str] = None, 
                  port: int = 22, key_file: Optional[str] = None, remote_path: str = '', **kwargs) -> Dict[str, Any]:
    """Crawl website via SFTP."""
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
