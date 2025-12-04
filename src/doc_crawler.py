import os
import time
import requests
from urllib.parse import urlparse
from typing import List, Set, Optional, Dict, Any, Callable
from collections import deque
import logging

from src.models.crawler_stats import CrawlerStats
from src.processors.config import HtmlProcessorConfig
from src.processors.html_processor import HtmlProcessor
from src.utils.url_utils import is_valid_url, url_to_filepath, should_add_to_queue
from src.utils.storage import StorageClient
from src.utils.robots import RobotsTxtChecker
from src.utils.rate_limiter import SimpleRateLimiter
from src.utils.retry import retry_on_http_error
from src.utils.sitemap import SitemapParser
from src.exceptions import InvalidURLError, ContentTooLargeError

logger = logging.getLogger('DocuCrawler')

DEFAULT_STATS_LOG_INTERVAL = 10
DEFAULT_MAX_CONTENT_LENGTH = 10 * 1024 * 1024
DEFAULT_CHUNK_SIZE = 8192
DEFAULT_TIMEOUT = 10
HTTP_OK = 200
DEFAULT_SINGLE_FILE_NAME = "documentation.md"

class DocuCrawler:
    """A general-purpose web crawler that converts HTML to Markdown."""
    
    def __init__(self, start_url: str, output_dir: str = "downloaded_docs", delay: float = 1.0,
                 max_pages: int = 0, timeout: int = DEFAULT_TIMEOUT, use_gcs: bool = False,
                 bucket_name: Optional[str] = None, project_id: Optional[str] = None,
                 credentials_path: Optional[str] = None, storage_config: Optional[Dict[str, Any]] = None,
                 single_file: bool = False, html_config_overrides: Optional[Dict[str, Any]] = None,
                 on_page_crawled: Optional[Callable[[str, int], None]] = None,
                 on_error: Optional[Callable[[str, Exception], None]] = None):
        """
        Initialize the web crawler.
        
        Args:
            start_url: Starting URL for crawling (must be valid HTTP/HTTPS URL)
            output_dir: Directory where files will be saved
            delay: Delay between requests in seconds (must be non-negative)
            max_pages: Maximum number of pages to crawl (0 for unlimited, must be non-negative)
            timeout: Request timeout in seconds (must be positive)
            use_gcs: Whether to use Google Cloud Storage (deprecated, use storage_config)
            bucket_name: GCS bucket name (deprecated, use storage_config)
            project_id: GCS project ID (deprecated, use storage_config)
            credentials_path: Path to GCS credentials (deprecated, use storage_config)
            storage_config: Storage configuration dictionary
            single_file: Whether to combine all pages into a single Markdown file
            html_config_overrides: Optional overrides for HtmlProcessorConfig
            on_page_crawled: Optional callback function called when a page is successfully crawled.
                            Receives (url: str, page_count: int) as arguments.
            on_error: Optional callback function called when an error occurs.
                      Receives (url: str, error: Exception) as arguments.
            
        Raises:
            ValueError: If input parameters are invalid
        """
        if not start_url or not isinstance(start_url, str):
            raise InvalidURLError("start_url must be a non-empty string")
        if not start_url.startswith(('http://', 'https://')):
            raise InvalidURLError("start_url must be a valid HTTP or HTTPS URL")
        if delay < 0:
            raise ValueError("delay must be non-negative")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if max_pages < 0:
            raise ValueError("max_pages must be non-negative")
        if not output_dir or not isinstance(output_dir, str):
            raise ValueError("output_dir must be a non-empty string")
        
        self.start_url = start_url
        self.delay = delay
        self.max_pages = max_pages
        self.timeout = timeout
        self.single_file = single_file
        
        parsed_url = urlparse(start_url)
        self.base_domain = parsed_url.netloc
        self.base_path = parsed_url.path
        
        self.visited_urls: Set[str] = set()
        self.urls_to_visit: deque = deque([start_url])
        self.urls_in_queue: Set[str] = {start_url}
        self.stats = CrawlerStats()
        self.max_content_length = DEFAULT_MAX_CONTENT_LENGTH
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        # Initialize config for HTML processor
        html_config_args = {
            'single_file': single_file,
            'base_url': start_url
        }
        if html_config_overrides:
            html_config_args.update(html_config_overrides)
            
        html_config = HtmlProcessorConfig(**html_config_args)
            
        self.html_processor = HtmlProcessor(config=html_config)
        self.robots_checker = RobotsTxtChecker(headers=self.headers, timeout=timeout)
        self.rate_limiter = SimpleRateLimiter(delay=delay)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._on_page_crawled_callback: Optional[Callable[[str, int], None]] = on_page_crawled
        self._on_error_callback: Optional[Callable[[str, Exception], None]] = on_error
        self.sitemap_parser = SitemapParser(session=self.session)
        
        # Check if start URL is a sitemap
        if start_url.lower().endswith('.xml') or 'sitemap' in start_url.lower():
            logger.info("Detected sitemap URL. Fetching URLs from sitemap...")
            sitemap_urls = self.sitemap_parser.fetch_urls(start_url)
            if sitemap_urls:
                logger.info(f"Found {len(sitemap_urls)} URLs in sitemap.")
                # Replace the queue with sitemap URLs (or append?)
                # Usually if sitemap is provided, we want to crawl those.
                # But start_url is usually the "root" for validation.
                # If start_url is sitemap.xml, we need a new base_domain/base_path maybe?
                # Actually, sitemap URLs are absolute.
                
                # If start_url was a sitemap, we might want to adjust base_domain/path
                # But let's keep the user's intent. 
                # If they gave a sitemap, they probably want to crawl those pages.
                
                # We need to add them to the queue.
                for url in sitemap_urls:
                    if url not in self.urls_in_queue and url not in self.visited_urls:
                        # Optional: Check valid url?
                        # If we strictly enforce base_domain of sitemap URL, it might match.
                        self.urls_to_visit.append(url)
                        self.urls_in_queue.add(url)
            else:
                logger.warning("No URLs found in sitemap.")
        
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
        
        # If single file mode is enabled, clear the output file if it exists
        if self.single_file:
            combined_file_path = DEFAULT_SINGLE_FILE_NAME
            # Try to clear the file if it exists
            try:
                if self.storage.exists(combined_file_path):
                    # For local storage, this effectively clears it. 
                    # For cloud, it overwrites with empty string or header.
                    self.storage.save_file(combined_file_path, f"# Documentation Crawl\nStarted: {time.strftime('%Y-%m-%d %H:%M:%S')}\nRoot: {self.start_url}\n\n")
            except Exception as e:
                logger.warning(f"Could not initialize single file: {e}")
            
        storage_info = f"storage type: {storage_config.get('storage_type', 'local' if not use_gcs else 'gcs')}" if storage_config else f"local directory: {output_dir}"
        logger.info(f"Crawler initialized with start URL: {start_url} ({storage_info})")
        logger.info(f"Base domain: {self.base_domain}, Base path: {self.base_path}")
        if self.single_file:
            logger.info("Single file mode enabled: All output will be combined into one file")
    
    def _call_error_callback(self, url: str, error: Exception) -> None:
        """
        Safely call error callback if set.
        
        Args:
            url: URL that caused the error
            error: Exception that occurred
        """
        if self._on_error_callback:
            try:
                self._on_error_callback(url, error)
            except Exception as callback_error:
                logger.warning(f"Error in error callback: {callback_error}")
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for crawling."""
        return is_valid_url(url, self.base_domain, self.base_path)
    
    def get_filepath(self, url: str) -> str:
        """Convert URL to file path."""
        return url_to_filepath(url, self.base_path, self.output_dir)
    
    def process_page(self, url: str, response: requests.Response) -> Optional[List[str]]:
        """Process downloaded page and extract links."""
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
            
            if self.single_file:
                # In single file mode, append to the main documentation file
                combined_file_path = DEFAULT_SINGLE_FILE_NAME
                
                # Add a clear header for the new page
                page_header = f"\n\n---\n\n# Source: {url}\n\n"
                content_to_append = page_header + text_content
                
                try:
                    self.storage.append_file(combined_file_path, content_to_append)
                except Exception as e:
                    logger.error(f"Failed to append to single file: {e}")
                    # Fallback to individual file save if single file fails
                    file_path = self.get_filepath(url)
                    self.storage.save_file(file_path, text_content)
            else:
                # Standard individual file mode
                file_path = self.get_filepath(url)
                self.storage.save_file(file_path, text_content)
                
            self.stats.pages_processed += 1
            logger.debug(f"Processed: {url} ({len(text_content)} characters)")
            
            # Call on_page_crawled callback if set
            if self._on_page_crawled_callback:
                try:
                    self._on_page_crawled_callback(url, self.stats.pages_processed)
                except Exception as callback_error:
                    logger.warning(f"Error in page crawled callback: {callback_error}")
            
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
                
                current_url = self.urls_to_visit.popleft()
                self.urls_in_queue.discard(current_url)
                
                if current_url in self.visited_urls:
                    continue
                
                user_agent = self.headers.get('User-Agent', '*')
                if not self.robots_checker.can_fetch(current_url, user_agent):
                    logger.debug(f"Skipping {current_url} - disallowed by robots.txt")
                    continue
                
                self.rate_limiter.wait_if_needed(self.base_domain)
                
                crawl_delay = self.robots_checker.get_crawl_delay(current_url, user_agent)
                delay_to_use = max(self.delay, crawl_delay) if crawl_delay else self.delay
                    
                logger.info(f"Crawling: {current_url}")
                
                try:
                    self.visited_urls.add(current_url)
                    response = self._fetch_url_with_retry(current_url)
                    
                    if response.status_code == HTTP_OK:
                        links = self.process_page(current_url, response)
                        if links:
                            for link in links:
                                if link not in self.visited_urls and link not in self.urls_in_queue:
                                    self.urls_to_visit.append(link)
                                    self.urls_in_queue.add(link)
                        
                        if self.stats.pages_processed % DEFAULT_STATS_LOG_INTERVAL == 0:
                            self._log_stats()
                    else:
                        self.stats.pages_failed += 1
                        logger.warning(f"Failed to retrieve {current_url}, status code: {response.status_code}")
                        error = requests.exceptions.RequestException(
                            f"HTTP {response.status_code} error for {current_url}"
                        )
                        self._call_error_callback(current_url, error)
                
                except requests.exceptions.RequestException as e:
                    self.stats.pages_failed += 1
                    error_msg = f"Request error for {current_url}: {str(e)}"
                    logger.error(error_msg)
                    self._call_error_callback(current_url, e)
                except Exception as e:
                    self.stats.pages_failed += 1
                    error_msg = f"Error processing {current_url}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    self._call_error_callback(current_url, e)
                
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
            self.session.close()
    
    @retry_on_http_error(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
    def _fetch_url_with_retry(self, url: str) -> requests.Response:
        """
        Fetch URL with automatic retry on HTTP errors.
        
        Args:
            url: URL to fetch
            
        Returns:
            Response object
            
        Raises:
            requests.exceptions.RequestException: If request fails after retries
            ContentTooLargeError: If response content exceeds max_content_length
        """
        response = self.session.get(url, timeout=self.timeout, verify=True, stream=True)
        
        content_length = response.headers.get('Content-Length')
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_content_length:
                    response.close()
                    raise ContentTooLargeError(f"Content length {size} exceeds maximum {self.max_content_length}")
            except ValueError:
                pass
        
        content = b''
        try:
            for chunk in response.iter_content(chunk_size=DEFAULT_CHUNK_SIZE):
                content += chunk
                if len(content) > self.max_content_length:
                    response.close()
                    raise ContentTooLargeError(f"Content exceeds maximum size {self.max_content_length}")
            
            response._content = content
            response.raw._content = content
        except ContentTooLargeError:
            raise
        except Exception as e:
            response.close()
            raise requests.exceptions.RequestException(f"Error reading response: {e}") from e
        
        return response
