import os
import time
import requests
from urllib.parse import urlparse
from typing import List, Set, Optional, Dict, Any, Callable
import logging

from src.models.crawler_stats import CrawlerStats
from src.processors.html_processor import HtmlProcessor
from src.utils.url_utils import is_valid_url, url_to_filepath, should_add_to_queue
from src.utils.storage import StorageClient
from src.utils.robots import RobotsTxtChecker
from src.utils.rate_limiter import SimpleRateLimiter
from src.utils.retry import retry_on_http_error

logger = logging.getLogger('DocuCrawler')

class DocuCrawler:
    """A general-purpose web crawler that converts HTML to Markdown."""
    
    def __init__(self, start_url: str, output_dir: str = "downloaded_docs", delay: float = 1.0,
                 max_pages: int = 0, timeout: int = 10, use_gcs: bool = False,
                 bucket_name: Optional[str] = None, project_id: Optional[str] = None,
                 credentials_path: Optional[str] = None, storage_config: Optional[Dict[str, Any]] = None):
        """Initialize the web crawler."""
        self.start_url = start_url
        self.delay = delay
        self.max_pages = max_pages
        self.timeout = timeout
        
        parsed_url = urlparse(start_url)
        self.base_domain = parsed_url.netloc
        self.base_path = parsed_url.path
        
        self.visited_urls: Set[str] = set()
        self.urls_to_visit: List[str] = [start_url]
        self.stats = CrawlerStats()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        self.html_processor = HtmlProcessor()
        
        # Initialize robots.txt checker
        self.robots_checker = RobotsTxtChecker()
        
        # Initialize rate limiter (use delay as the rate limit)
        self.rate_limiter = SimpleRateLimiter(delay=delay)
        
        # Error callback (can be set externally)
        self._on_error_callback: Optional[Callable[[str, Exception], None]] = None
        
        if storage_config:
            self.storage = StorageClient(**storage_config)
            storage_type = storage_config.get('storage_type', 'local')
            if storage_type == 'local':
                self.output_dir = storage_config.get('output', output_dir)
            else:
                self.output_dir = output_dir
        else:
            self.storage = StorageClient(
                use_gcs=use_gcs,
                bucket_name=bucket_name,
                credentials_path=credentials_path,
                project_id=project_id,
                output_dir=output_dir
            )
            self.output_dir = output_dir
        
        storage_info = f"storage type: {storage_config.get('storage_type', 'local' if not use_gcs else 'gcs')}" if storage_config else f"local directory: {output_dir}"
        logger.info(f"Crawler initialized with start URL: {start_url} ({storage_info})")
        logger.info(f"Base domain: {self.base_domain}, Base path: {self.base_path}")
    
    def is_valid_url(self, url: str) -> bool:
        """Wrapper around is_valid_url utility function."""
        return is_valid_url(url, self.base_domain, self.base_path)
    
    def get_filepath(self, url: str) -> str:
        """Wrapper around url_to_filepath utility function."""
        return url_to_filepath(url, self.base_path, self.output_dir)
    
    def process_page(self, url: str, response: requests.Response) -> Optional[List[str]]:
        """Process a downloaded page."""
        try:
            content_type = response.headers.get('Content-Type', '').lower()
            content_length = len(response.content)
            self.stats.bytes_downloaded += content_length
            
            if 'text/html' not in content_type:
                logger.warning(f"Skipping non-HTML content: {url} (Content-Type: {content_type})")
                return None
                
            text_content = self.html_processor.extract_text(
                response.text, 
                url=url
            )
            
            file_path = self.get_filepath(url)
            self.storage.save_file(file_path, text_content)
                
            self.stats.pages_processed += 1
            logger.debug(f"Processed: {url} ({len(text_content)} characters)")
            
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
                if self.max_pages > 0 and self.stats.pages_processed >= self.max_pages:
                    logger.info(f"Reached maximum number of pages: {self.max_pages}")
                    break
                
                current_url = self.urls_to_visit.pop(0)
                
                if current_url in self.visited_urls:
                    continue
                
                # Check robots.txt before crawling
                user_agent = self.headers.get('User-Agent', '*')
                if not self.robots_checker.can_fetch(current_url, user_agent):
                    logger.debug(f"Skipping {current_url} - disallowed by robots.txt")
                    continue
                
                # Apply rate limiting
                self.rate_limiter.wait_if_needed(self.base_domain)
                
                # Get crawl delay from robots.txt (if specified)
                crawl_delay = self.robots_checker.get_crawl_delay(current_url, user_agent)
                delay_to_use = max(self.delay, crawl_delay) if crawl_delay else self.delay
                    
                logger.info(f"Crawling: {current_url}")
                
                try:
                    self.visited_urls.add(current_url)
                    # Use retry decorator for HTTP requests
                    response = self._fetch_url_with_retry(current_url)
                    
                    if response.status_code == 200:
                        links = self.process_page(current_url, response)
                        if links:
                            for link in links:
                                if should_add_to_queue(link, self.visited_urls, self.urls_to_visit):
                                    self.urls_to_visit.append(link)
                        
                        if self.stats.pages_processed % 10 == 0:
                            self._log_stats()
                    else:
                        self.stats.pages_failed += 1
                        logger.warning(f"Failed to retrieve {current_url}, status code: {response.status_code}")
                        if self._on_error_callback:
                            try:
                                # Create an appropriate exception for non-200 status codes
                                error = requests.exceptions.RequestException(
                                    f"HTTP {response.status_code} error for {current_url}"
                                )
                                self._on_error_callback(current_url, error)
                            except Exception as callback_error:
                                logger.warning(f"Error in error callback: {callback_error}")
                
                except requests.exceptions.RequestException as e:
                    self.stats.pages_failed += 1
                    error_msg = f"Request error for {current_url}: {str(e)}"
                    logger.error(error_msg)
                    if self._on_error_callback:
                        try:
                            self._on_error_callback(current_url, e)
                        except Exception as callback_error:
                            logger.warning(f"Error in error callback: {callback_error}")
                except Exception as e:
                    self.stats.pages_failed += 1
                    error_msg = f"Error processing {current_url}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    if self._on_error_callback:
                        try:
                            self._on_error_callback(current_url, e)
                        except Exception as callback_error:
                            logger.warning(f"Error in error callback: {callback_error}")
                
                # Use the delay (which may be overridden by robots.txt crawl_delay)
                time.sleep(delay_to_use)
            
            self._log_stats(final=True)
            
        except KeyboardInterrupt:
            logger.info("Crawling stopped by user (Ctrl+C)")
            self._log_stats(final=True)
        except Exception as e:
            logger.critical(f"Critical error during crawl: {str(e)}", exc_info=True)
            self._log_stats(final=True)
    
    def _log_stats(self, final: bool = False) -> None:
        """Log statistics about the crawl progress."""
        elapsed_time = time.time() - self.stats.start_time
        elapsed_min = elapsed_time / 60
        
        pages_per_min = self.stats.pages_processed / elapsed_min if elapsed_min > 0 else 0
        mb_downloaded = self.stats.bytes_downloaded / (1024 * 1024)
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
    
    @retry_on_http_error(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
    def _fetch_url_with_retry(self, url: str) -> requests.Response:
        """Fetch URL with automatic retry on HTTP errors."""
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=True)
