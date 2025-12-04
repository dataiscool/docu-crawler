import logging
import xml.etree.ElementTree as ET
from typing import List, Set, Optional
from urllib.parse import urlparse
import requests

logger = logging.getLogger('DocuCrawler')

class SitemapParser:
    """
    Parser for XML sitemaps to extract URLs for crawling.
    """
    
    def __init__(self, session: Optional[requests.Session] = None):
        """
        Initialize sitemap parser.
        
        Args:
            session: Optional requests session to use for fetching
        """
        self.session = session or requests.Session()
        self.namespaces = {
            'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'
        }
        
    def fetch_urls(self, sitemap_url: str, visited: Optional[Set[str]] = None, max_depth: int = 10) -> List[str]:
        """
        Fetch and parse a sitemap to extract all URLs.
        Handles nested sitemaps (sitemapindex).
        
        Args:
            sitemap_url: URL of the sitemap.xml
            visited: Set of already visited sitemap URLs (to prevent infinite recursion)
            max_depth: Maximum depth for nested sitemaps (default: 10)
            
        Returns:
            List of URLs found in the sitemap
        """
        if visited is None:
            visited = set()
        
        if max_depth <= 0:
            logger.warning(f"Maximum sitemap depth reached for {sitemap_url} (sitemap inception detected)")
            return []
        
        if sitemap_url in visited:
            logger.warning(f"Circular reference detected in sitemap: {sitemap_url} (sitemaps referencing themselves - classic)")
            return []
        
        visited.add(sitemap_url)
        urls: Set[str] = set()
        
        try:
            logger.info(f"Fetching sitemap: {sitemap_url}")
            response = self.session.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            # Decode content, utf-8 then latin-1
            try:
                content_text = response.content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content_text = response.content.decode('latin-1')
                except UnicodeDecodeError:
                    logger.error(f"Could not decode sitemap content from {sitemap_url}")
                    return list(urls)
            
            # What kind of sitemap is this?
            if '<sitemapindex' in content_text:
                self._parse_index(response.content, urls, visited, max_depth)
            elif '<urlset' in content_text:
                self._parse_urlset(response.content, urls)
            else:
                logger.warning(f"Unknown sitemap format at {sitemap_url} (not XML, not sitemap index - mystery format)")
                
        except Exception as e:
            logger.error(f"Error processing sitemap {sitemap_url}: {str(e)}")
            
        return list(urls)

    def _parse_urlset(self, content: bytes, urls: Set[str]):
        """Parse a standard urlset sitemap."""
        try:
            root = ET.fromstring(content)
            # XML namespaces. Some sitemaps use them, some don't.
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Check for namespace first
            locs = root.findall('.//ns:loc', ns)
            if not locs:
                # No namespace found, try without it
                locs = root.findall('.//loc')
                
            for loc in locs:
                if loc.text:
                    url = loc.text.strip()
                    urls.add(url)
                    
        except ET.ParseError as e:
            logger.error(f"XML parse error in urlset: {e}")

    def _parse_index(self, content: bytes, urls: Set[str], visited: Set[str], max_depth: int):
        """Parse a sitemap index (nested sitemaps)."""
        try:
            root = ET.fromstring(content)
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            sitemaps = root.findall('.//ns:loc', ns)
            if not sitemaps:
                sitemaps = root.findall('.//loc')
                
            for loc in sitemaps:
                if loc.text:
                    sub_sitemap_url = loc.text.strip()
                    # Recursively fetch sub sitemaps, but watch the depth
                    sub_urls = self.fetch_urls(sub_sitemap_url, visited, max_depth - 1)
                    urls.update(sub_urls)
                    
        except ET.ParseError as e:
            logger.error(f"XML parse error in sitemap index: {e}")

