from dataclasses import dataclass, field
import time

@dataclass
class CrawlerStats:
    """Statistics about the crawling process."""
    pages_processed: int = 0
    pages_failed: int = 0
    bytes_downloaded: int = 0
    start_time: float = field(default_factory=time.time)
