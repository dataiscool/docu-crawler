from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

@dataclass
class PageResult:
    """Result for a single crawled page."""
    url: str
    status_code: int
    success: bool
    file_path: Optional[str] = None
    error: Optional[str] = None
    bytes_downloaded: int = 0
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

@dataclass
class CrawlResult:
    """Complete crawl results and statistics."""
    pages_crawled: int = 0
    pages_failed: int = 0
    urls_visited: int = 0
    bytes_downloaded: int = 0
    elapsed_time: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)
    page_results: List[PageResult] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        total = self.pages_crawled + self.pages_failed
        if total == 0:
            return 0.0
        return (self.pages_crawled / total) * 100
    
    @property
    def pages_per_minute(self) -> float:
        """Calculate pages per minute."""
        if self.elapsed_time == 0:
            return 0.0
        return (self.pages_crawled / self.elapsed_time) * 60
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        # Convert datetime objects to ISO format strings
        if isinstance(result['start_time'], datetime):
            result['start_time'] = result['start_time'].isoformat()
        if isinstance(result['end_time'], datetime):
            result['end_time'] = result['end_time'].isoformat()
        # Convert page results
        result['page_results'] = [pr.to_dict() for pr in self.page_results]
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def summary(self) -> str:
        """Get a human-readable summary."""
        return (
            f"Crawl Summary:\n"
            f"  Pages crawled: {self.pages_crawled}\n"
            f"  Pages failed: {self.pages_failed}\n"
            f"  URLs visited: {self.urls_visited}\n"
            f"  Bytes downloaded: {self.bytes_downloaded / (1024*1024):.2f} MB\n"
            f"  Success rate: {self.success_rate:.1f}%\n"
            f"  Speed: {self.pages_per_minute:.1f} pages/min\n"
            f"  Elapsed time: {self.elapsed_time / 60:.1f} minutes"
        )

