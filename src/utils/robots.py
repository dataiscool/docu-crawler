import logging
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from typing import Dict, Optional, List
import time
import requests

logger = logging.getLogger('DocuCrawler')

DEFAULT_CACHE_DURATION = 3600

# HTTP status codes
HTTP_OK = 200
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403

class RobotsTxtChecker:
    """
    Check and respect robots.txt files.
    """
    
    def __init__(self, headers: Optional[Dict[str, str]] = None, timeout: int = 10):
        """
        Initialize robots.txt checker.
        
        Args:
            headers: Headers to use for fetching robots.txt (e.g. User-Agent)
            timeout: Timeout in seconds for fetching robots.txt
        """
        self.parsers: Dict[str, RobotFileParser] = {}
        self.cache_time: Dict[str, float] = {}
        self.cache_duration = DEFAULT_CACHE_DURATION
        self.headers = headers or {'User-Agent': '*'}
        self.timeout = timeout
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _get_robots_url(self, url: str) -> str:
        """Get robots.txt URL for a given URL."""
        domain = self._get_domain(url)
        return f"{domain}/robots.txt"
    
    def _get_parser(self, url: str) -> RobotFileParser:
        """Get or create RobotFileParser for a domain."""
        domain = self._get_domain(url)
        
        if domain in self.parsers:
            cache_age = time.time() - self.cache_time.get(domain, 0)
            if cache_age < self.cache_duration:
                return self.parsers[domain]
        
        robots_url = self._get_robots_url(url)
        parser = RobotFileParser()
        parser.set_url(robots_url)
        
        try:
            # Use requests to fetch robots.txt to respect timeouts and headers
            response = requests.get(robots_url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code in (HTTP_UNAUTHORIZED, HTTP_FORBIDDEN):
                # If access forbidden, assume disallowed (standard practice)
                # However, RobotFileParser default is allow all if read fails.
                # To be strict: disallow all. To be permissive: allow all.
                # Googlebot treats 403 as "full allow" or "full disallow"? 
                # Actually, 4xx usually means "no robots.txt" -> allow.
                # But 401/403 specifically means auth/forbidden.
                # We'll stick to standard behavior: if we can't read it, we usually default to allow,
                # unless we want to simulate an empty disallow list.
                # Let's log and proceed with empty parser (allow all).
                logger.warning(f"Access denied for robots.txt at {robots_url} ({response.status_code})")
                
            elif response.status_code == HTTP_OK:
                # Decode content safely, handling encoding issues
                try:
                    content_text = response.text
                except (UnicodeDecodeError, AttributeError):
                    try:
                        content_text = response.content.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            content_text = response.content.decode('latin-1')
                        except UnicodeDecodeError:
                            logger.warning(f"Could not decode robots.txt content from {robots_url}")
                            content_text = ''
                
                lines = content_text.splitlines()
                parser.parse(lines)
                logger.debug(f"Loaded robots.txt from {robots_url}")
                
        except Exception as e:
            logger.warning(f"Could not load robots.txt from {robots_url}: {str(e)}")
            # Fallback to allow all (default state of new RobotFileParser)
        
        self.parsers[domain] = parser
        self.cache_time[domain] = time.time()
        
        return parser
    
    def can_fetch(self, url: str, user_agent: str = '*') -> bool:
        """
        Check if a URL can be fetched according to robots.txt.
        
        Args:
            url: URL to check
            user_agent: User agent string (default: '*')
            
        Returns:
            True if URL can be fetched, False otherwise
        """
        try:
            parser = self._get_parser(url)
            parsed_url = urlparse(url)
            path = parsed_url.path or '/'
            
            can_fetch = parser.can_fetch(user_agent, url)
            
            if not can_fetch:
                logger.debug(f"robots.txt disallows fetching: {url}")
            
            return can_fetch
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {str(e)}")
            return True
    
    def get_crawl_delay(self, url: str, user_agent: str = '*') -> Optional[float]:
        """
        Get crawl delay from robots.txt.
        
        Args:
            url: URL to check
            user_agent: User agent string (default: '*')
            
        Returns:
            Crawl delay in seconds, or None if not specified
        """
        try:
            parser = self._get_parser(url)
            delay = parser.crawl_delay(user_agent)
            if delay:
                logger.debug(f"robots.txt specifies crawl delay of {delay}s for {url}")
            return delay
        except Exception as e:
            logger.warning(f"Error getting crawl delay for {url}: {str(e)}")
            return None

