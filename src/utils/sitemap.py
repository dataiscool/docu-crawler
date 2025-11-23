import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger('DocuCrawler')

class SitemapGenerator:
    """Generate sitemap.xml files for crawled content."""
    
    def __init__(self, base_url: str = ''):
        """
        Initialize sitemap generator.
        
        Args:
            base_url: Base URL for the sitemap (e.g., https://docs.example.com)
        """
        self.base_url = base_url.rstrip('/')
        self.urls: List[Dict[str, any]] = []
    
    def add_url(self, url_path: str, lastmod: Optional[datetime] = None, 
                changefreq: str = 'weekly', priority: float = 0.5) -> None:
        """
        Add a URL to the sitemap.
        
        Args:
            url_path: Relative path or full URL
            lastmod: Last modification date
            changefreq: Change frequency (always, hourly, daily, weekly, monthly, yearly, never)
            priority: Priority (0.0 to 1.0)
        """
        # If it's already a full URL, use it; otherwise construct from base_url
        if url_path.startswith('http'):
            full_url = url_path
        else:
            full_url = f"{self.base_url}/{url_path.lstrip('/')}"
        
        self.urls.append({
            'loc': full_url,
            'lastmod': lastmod or datetime.now(),
            'changefreq': changefreq,
            'priority': priority
        })
    
    def generate_xml(self) -> str:
        """
        Generate sitemap.xml content.
        
        Returns:
            XML string for sitemap
        """
        # Create root element
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        # Add URLs
        for url_data in self.urls:
            url_elem = ET.SubElement(urlset, 'url')
            
            # Location
            loc_elem = ET.SubElement(url_elem, 'loc')
            loc_elem.text = url_data['loc']
            
            # Last modification
            if url_data['lastmod']:
                lastmod_elem = ET.SubElement(url_elem, 'lastmod')
                if isinstance(url_data['lastmod'], datetime):
                    lastmod_elem.text = url_data['lastmod'].strftime('%Y-%m-%d')
                else:
                    lastmod_elem.text = str(url_data['lastmod'])
            
            # Change frequency
            changefreq_elem = ET.SubElement(url_elem, 'changefreq')
            changefreq_elem.text = url_data['changefreq']
            
            # Priority
            priority_elem = ET.SubElement(url_elem, 'priority')
            priority_elem.text = str(url_data['priority'])
        
        # Convert to string
        ET.indent(urlset, space='  ')
        return ET.tostring(urlset, encoding='unicode', xml_declaration=True)
    
    def save(self, file_path: str) -> None:
        """
        Save sitemap to file.
        
        Args:
            file_path: Path where to save the sitemap
        """
        xml_content = self.generate_xml()
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(xml_content, encoding='utf-8')
        logger.info(f"Saved sitemap with {len(self.urls)} URLs to {file_path}")

def generate_robots_txt(content: str, file_path: str) -> None:
    """
    Generate a robots.txt file.
    
    Args:
        content: Content for robots.txt
        file_path: Path where to save robots.txt
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    logger.info(f"Saved robots.txt to {file_path}")

def create_default_robots_txt(sitemap_url: Optional[str] = None) -> str:
    """
    Create a default robots.txt file content.
    
    Args:
        sitemap_url: URL to sitemap.xml (optional)
        
    Returns:
        robots.txt content
    """
    content = "User-agent: *\n"
    content += "Allow: /\n"
    
    if sitemap_url:
        content += f"\nSitemap: {sitemap_url}\n"
    
    return content

