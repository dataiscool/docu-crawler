import os
import time
import requests
from urllib.parse import urlparse
from typing import List, Set, Optional, Dict, Any
import logging

from src.models.crawler_stats import CrawlerStats
from src.processors.html_processor import HtmlProcessor
from src.utils.url_utils import is_valid_url, url_to_filepath, should_add_to_queue
from src.utils.storage import StorageClient

logger = logging.getLogger('DocCrawler')

class DocCrawler:
    """A web crawler for documentation sites that converts HTML to Markdown."""
    
    def __init__(self, start_url: str, output_dir: str = "downloaded_docs", delay: float = 1.0,
                 max_pages: int = 0, timeout: int = 10, use_gcs: bool = False,
                 bucket_name: Optional[str] = None, project_id: Optional[str] = None,
                 credentials_path: Optional[str] = None):
        """
        Initialize the documentation crawler.
        
        Args:
            start_url: The starting URL of the documentation
            output_dir: Directory where downloaded files will be saved
            delay: Delay between requests in seconds
            max_pages: Maximum number of pages to download (0 for unlimited)
            timeout: Request timeout in seconds
            use_gcs: Whether to use Google Cloud Storage for file storage
            bucket_name: GCS bucket name (required if use_gcs is True)
            project_id: Google Cloud project ID (optional)
            credentials_path: Path to GCS credentials JSON file
        """
        self.start_url = start_url
        self.output_dir = output_dir
        self.delay = delay
        self.max_pages = max_pages
        self.timeout = timeout
        
        # Extract the base domain to ensure we stay within the same documentation
        parsed_url = urlparse(start_url)
        self.base_domain = parsed_url.netloc
        self.base_path = parsed_url.path
        
        # Initialize URL tracking
        self.visited_urls: Set[str] = set()
        self.urls_to_visit: List[str] = [start_url]
        
        # Stats for logging
        self.stats = CrawlerStats()
            
        # Define headers to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        # Initialize HTML processor
        self.html_processor = HtmlProcessor()
        
        # Initialize storage client
        self.storage = StorageClient(
            use_gcs=use_gcs,
            bucket_name=bucket_name,
            credentials_path=credentials_path,
            project_id=project_id,
            output_dir=output_dir
        )
        
        if use_gcs:
            logger.info(f"Crawler initialized with start URL: {start_url} (storing to GCS bucket: {bucket_name})")
        else:
            logger.info(f"Crawler initialized with start URL: {start_url} (storing to local directory: {output_dir})")
            
        logger.info(f"Base domain: {self.base_domain}, Base path: {self.base_path}")
    
    def is_valid_url(self, url: str) -> bool:
        """Wrapper around is_valid_url utility function."""
        return is_valid_url(url, self.base_domain, self.base_path)
    
    def get_filepath(self, url: str) -> str:
        """Wrapper around url_to_filepath utility function."""
        return url_to_filepath(url, self.base_path, self.output_dir)
    
    def process_page(self, url: str, response: requests.Response) -> Optional[List[str]]:
        """
        Process a downloaded page.
        
        Args:
            url: The URL of the page
            response: The HTTP response
            
        Returns:
            List of extracted URLs or None if processing failed
        """
        try:
            # Get the content type
            content_type = response.headers.get('Content-Type', '').lower()
            content_length = len(response.content)
            self.stats.bytes_downloaded += content_length
            
            # Process only HTML content
            if 'text/html' not in content_type:
                logger.warning(f"Skipping non-HTML content: {url} (Content-Type: {content_type})")
                return None
                
            # Extract text content
            text_content = self.html_processor.extract_text(response.text)
            
            # Save to storage (local or GCS)
            file_path = self.get_filepath(url)
            self.storage.save_file(file_path, text_content)
                
            self.stats.pages_processed += 1
            logger.debug(f"Processed: {url} ({len(text_content)} characters)")
            
            # Extract links
            links = self.html_processor.extract_links(
                response.text, 
                url, 
                lambda u: self.is_valid_url(u) and u not in self.visited_urls
            )
            
            new_links = sum(1 for link in links if link not in self.urls_to_visit)
            logger.debug(f"Found {len(links)} links, {new_links} new")
            
            return links
        except Exception as e:
            logger.error(f"Error processing page {url}: {str(e)}", exc_info=True)
            self.stats.pages_failed += 1
            return None
    
    def crawl(self) -> None:
        """Start the crawling process."""
        logger.info(f"Starting crawl from {self.start_url}")
        logger.info(f"Files will be saved to {os.path.abspath(self.output_dir)}")
        
        try:
            while self.urls_to_visit:
                # Check if we've reached the maximum number of pages
                if self.max_pages > 0 and self.stats.pages_processed >= self.max_pages:
                    logger.info(f"Reached maximum number of pages: {self.max_pages}")
                    break
                
                # Get the next URL to visit
                current_url = self.urls_to_visit.pop(0)
                
                # Skip if already visited
                if current_url in self.visited_urls:
                    continue
                    
                logger.info(f"Crawling: {current_url}")
                
                try:
                    # Add to visited set
                    self.visited_urls.add(current_url)
                    
                    # Send a GET request
                    response = requests.get(current_url, headers=self.headers, timeout=self.timeout, verify=False)
                    
                    # If the request was successful
                    if response.status_code == 200:
                        links = self.process_page(current_url, response)
                        if links:
                            # Add new links to the queue
                            for link in links:
                                if should_add_to_queue(link, self.visited_urls, self.urls_to_visit):
                                    self.urls_to_visit.append(link)
                        
                        # Log progress statistics periodically
                        if self.stats.pages_processed % 10 == 0:
                            self._log_stats()
                    else:
                        self.stats.pages_failed += 1
                        logger.warning(f"Failed to retrieve {current_url}, status code: {response.status_code}")
                
                except requests.exceptions.RequestException as e:
                    self.stats.pages_failed += 1
                    logger.error(f"Request error for {current_url}: {str(e)}")
                except Exception as e:
                    self.stats.pages_failed += 1
                    logger.error(f"Error processing {current_url}: {str(e)}", exc_info=True)
                
                # Be respectful to the server
                time.sleep(self.delay)
                
            # Final statistics
            self._log_stats(final=True)
            
        except KeyboardInterrupt:
            logger.info("Crawling stopped by user (Ctrl+C)")
            self._log_stats(final=True)
        except Exception as e:
            logger.critical(f"Critical error during crawl: {str(e)}", exc_info=True)
            self._log_stats(final=True)
    
    def _log_stats(self, final: bool = False) -> None:
        """
        Log statistics about the crawl progress.
        
        Args:
            final: Whether this is the final statistics output
        """
        elapsed_time = time.time() - self.stats.start_time
        elapsed_min = elapsed_time / 60
        
        # Calculate pages per minute
        pages_per_min = self.stats.pages_processed / elapsed_min if elapsed_min > 0 else 0
        
        # Calculate downloaded data
        mb_downloaded = self.stats.bytes_downloaded / (1024 * 1024)
        
        # Remaining URLs
        remaining_urls = len(self.urls_to_visit)
        
        if final:
            logger.info("=== Crawling completed ===")
        
        logger.info(
            f"Stats: Processed {self.stats.pages_processed} pages "
            f"({pages_per_min:.1f} pages/min), "
            f"Failed: {self.stats.pages_failed}, "
            f"Downloaded: {mb_downloaded:.2f} MB, "
            f"Elapsed: {elapsed_min:.1f} minutes"
        )
        
        if remaining_urls > 0 and not final:
            logger.info(f"Remaining URLs to visit: {remaining_urls}")
        
        if final:
            logger.info(f"Total URLs processed: {len(self.visited_urls)}")
            logger.info(f"Output directory: {os.path.abspath(self.output_dir)}")
            logger.info(f"Log file: {os.path.abspath('doc_crawler.log')}")