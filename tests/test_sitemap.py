import unittest
from unittest.mock import Mock, MagicMock
import xml.etree.ElementTree as ET
from src.utils.sitemap import SitemapParser

class TestSitemapParser(unittest.TestCase):
    """Test cases for SitemapParser."""

    def setUp(self):
        self.mock_session = MagicMock()
        self.parser = SitemapParser(session=self.mock_session)

    def test_parse_urlset(self):
        """Test parsing a standard urlset sitemap."""
        xml_content = b"""
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>http://example.com/page1</loc>
            </url>
            <url>
                <loc>http://example.com/page2</loc>
            </url>
        </urlset>
        """
        urls = set()
        self.parser._parse_urlset(xml_content, urls)
        self.assertIn("http://example.com/page1", urls)
        self.assertIn("http://example.com/page2", urls)
        self.assertEqual(len(urls), 2)

    def test_parse_index(self):
        """Test parsing a sitemap index."""
        # mock response for sub-sitemap
        mock_response = Mock()
        mock_response.text = "<urlset><url><loc>http://example.com/subpage</loc></url></urlset>"
        mock_response.content = mock_response.text.encode('utf-8')
        mock_response.status_code = 200
        self.mock_session.get.return_value = mock_response

        xml_content = b"""
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap>
                <loc>http://example.com/sitemap1.xml</loc>
            </sitemap>
        </sitemapindex>
        """
        urls = set()
        visited = set()
        max_depth = 10
        self.parser._parse_index(xml_content, urls, visited, max_depth)
        
        # verify sub-sitemap was fetched
        self.mock_session.get.assert_called_with("http://example.com/sitemap1.xml", timeout=30)
        self.assertIn("http://example.com/subpage", urls)

    def test_malformed_xml(self):
        """Test handling of malformed XML."""
        urls = set()
        self.parser._parse_urlset(b"not xml", urls)
        self.assertEqual(len(urls), 0) # should not crash, just find nothing

if __name__ == '__main__':
    unittest.main()

