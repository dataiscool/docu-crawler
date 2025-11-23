import logging
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from typing import Dict, Optional
import time

logger = logging.getLogger('DocuCrawler')

class RobotsTxtChecker:
    """
    Check and respect robots.txt files.
    """
    
    def __init__(self):
        """Initialize robots.txt checker."""
        self.parsers: Dict[str, RobotFileParser] = {}
        self.cache_time: Dict[str, float] = {}
        self.cache_duration = 3600  # Cache for 1 hour
    
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
        
        # Check cache
        if domain in self.parsers:
            cache_age = time.time() - self.cache_time.get(domain, 0)
            if cache_age < self.cache_duration:
                return self.parsers[domain]
        
        # Create new parser
        robots_url = self._get_robots_url(url)
        parser = RobotFileParser()
        parser.set_url(robots_url)
        
        try:
            parser.read()
            logger.debug(f"Loaded robots.txt from {robots_url}")
        except Exception as e:
            logger.warning(f"Could not load robots.txt from {robots_url}: {str(e)}")
            # Create a permissive parser if robots.txt can't be loaded
            parser = RobotFileParser()
            parser.set_url(robots_url)
        
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
            # Default to allowing if there's an error
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

