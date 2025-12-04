import time
import logging
from typing import Callable, TypeVar, Optional
from functools import wraps

logger = logging.getLogger('DocuCrawler')

T = TypeVar('T')

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    retry_on: Optional[tuple] = None
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Factor to multiply delay by on each retry
        max_delay: Maximum delay in seconds
        retry_on: Tuple of exception types to retry on (default: all exceptions)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if retry_on and not isinstance(e, retry_on):
                        raise
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
                        raise last_exception
            
            # Should never get here but type checkers need this
            raise RuntimeError("Unexpected error in retry decorator")
        
        return wrapper
    return decorator

def retry_on_http_error(
    max_retries: int = 3,
    retry_status_codes: tuple = (500, 502, 503, 504, 429),
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
):
    """
    Retry function specifically for HTTP requests.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_status_codes: HTTP status codes to retry on
        initial_delay: Initial delay in seconds
        backoff_factor: Factor to multiply delay by on each retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if hasattr(result, 'status_code'):
                        if result.status_code in retry_status_codes:
                            if attempt < max_retries:
                                retry_after = result.headers.get('Retry-After')
                                if retry_after:
                                    try:
                                        delay = float(retry_after)
                                    except ValueError:
                                        pass
                                
                                logger.warning(
                                    f"HTTP {result.status_code} error on attempt {attempt + 1}/{max_retries + 1}. "
                                    f"Retrying in {delay:.1f}s..."
                                )
                                time.sleep(delay)
                                delay = min(delay * backoff_factor, 60.0)
                                continue
                    return result
                except Exception as e:
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay = min(delay * backoff_factor, 60.0)
                    else:
                        raise
            
            raise RuntimeError("Unexpected error in retry decorator")
        
        return wrapper
    return decorator

