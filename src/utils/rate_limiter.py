import time
import logging
from typing import Dict, Optional
from collections import defaultdict
from threading import Lock

logger = logging.getLogger('DocuCrawler')

class RateLimiter:
    """
    Rate limiter using token bucket algorithm.
    Supports per-domain rate limiting.
    """
    
    def __init__(self, rate: float = 1.0, per: float = 1.0, per_domain: bool = True):
        """
        Initialize rate limiter.
        
        Args:
            rate: Number of requests allowed
            per: Time period in seconds
            per_domain: Whether to limit per domain or globally
        """
        self.rate = rate
        self.per = per
        self.per_domain = per_domain
        self.tokens: Dict[str, float] = defaultdict(lambda: rate)
        self.last_update: Dict[str, float] = defaultdict(lambda: time.time())
        self.lock = Lock()
    
    def wait_if_needed(self, domain: Optional[str] = None) -> None:
        """
        Wait if necessary to respect rate limit.
        
        Args:
            domain: Domain name for per-domain limiting (optional)
        """
        key = domain if self.per_domain and domain else 'global'
        
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update[key]
            
            tokens_to_add = (elapsed / self.per) * self.rate
            self.tokens[key] = min(self.tokens[key] + tokens_to_add, self.rate)
            self.last_update[key] = now
            
            if self.tokens[key] < 1.0:
                wait_time = (1.0 - self.tokens[key]) * (self.per / self.rate)
                logger.debug(f"Rate limit reached for {key}, waiting {wait_time:.2f}s")
                time.sleep(wait_time)
                now = time.time()
                elapsed = now - self.last_update[key]
                tokens_to_add = (elapsed / self.per) * self.rate
                self.tokens[key] = min(self.tokens[key] + tokens_to_add, self.rate)
                self.last_update[key] = now
            
            self.tokens[key] -= 1.0

class SimpleRateLimiter:
    """
    Simple rate limiter that just enforces a delay between requests.
    """
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize simple rate limiter.
        
        Args:
            delay: Delay in seconds between requests
        """
        self.delay = delay
        self.last_request_time: Dict[str, float] = {}
        self.lock = Lock()
    
    def wait_if_needed(self, domain: Optional[str] = None) -> None:
        """
        Wait if necessary to respect rate limit.
        
        Args:
            domain: Domain name (optional, for per-domain limiting)
        """
        key = domain or 'global'
        
        with self.lock:
            now = time.time()
            if key in self.last_request_time:
                elapsed = now - self.last_request_time[key]
                if elapsed < self.delay:
                    wait_time = self.delay - elapsed
                    logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                    time.sleep(wait_time)
            
            self.last_request_time[key] = time.time()

