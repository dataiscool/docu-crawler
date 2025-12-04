"""Tests for DocuCrawler class."""
import unittest
from unittest.mock import Mock, patch, MagicMock
from src.doc_crawler import DocuCrawler
from src.exceptions import InvalidURLError, ContentTooLargeError


class TestDocuCrawler(unittest.TestCase):
    """Test cases for DocuCrawler class."""
    
    def test_init_valid_url(self):
        """Test initialization with valid URL."""
        crawler = DocuCrawler("https://example.com")
        self.assertEqual(crawler.start_url, "https://example.com")
        self.assertEqual(crawler.delay, 1.0)
        self.assertEqual(crawler.max_pages, 0)
        self.assertEqual(crawler.timeout, 10)
    
    def test_init_invalid_url_not_string(self):
        """Test initialization with non-string URL."""
        with self.assertRaises(InvalidURLError):
            DocuCrawler(None)
    
    def test_init_invalid_url_not_http(self):
        """Test initialization with non-HTTP URL."""
        with self.assertRaises(InvalidURLError):
            DocuCrawler("ftp://example.com")
    
    def test_init_invalid_delay(self):
        """Test initialization with negative delay."""
        with self.assertRaises(ValueError):
            DocuCrawler("https://example.com", delay=-1.0)
    
    def test_init_invalid_timeout(self):
        """Test initialization with non-positive timeout."""
        with self.assertRaises(ValueError):
            DocuCrawler("https://example.com", timeout=0)
    
    def test_init_invalid_max_pages(self):
        """Test initialization with negative max_pages."""
        with self.assertRaises(ValueError):
            DocuCrawler("https://example.com", max_pages=-1)
    
    def test_init_invalid_output_dir(self):
        """Test initialization with invalid output_dir."""
        with self.assertRaises(ValueError):
            DocuCrawler("https://example.com", output_dir="")
    
    def test_fetch_url_content_too_large(self):
        """Test that content exceeding max size raises error."""
        crawler = DocuCrawler("https://example.com")
        crawler.max_content_length = 100  # small limit
        
        # Mock the session.get method
        mock_response = Mock()
        mock_response.headers = {'Content-Length': '200'}
        mock_response.close = Mock()
        # iter_content needs to be a callable that returns an iterator
        mock_response.iter_content = Mock(return_value=iter([b'x' * 101]))  # Simulate content exceeding limit
        mock_response._content = None
        mock_response.raw = Mock()
        mock_response.raw._content = None
        
        crawler.session.get = Mock(return_value=mock_response)
        
        with self.assertRaises(ContentTooLargeError):
            crawler._fetch_url_with_retry("https://example.com")
    
    def test_call_error_callback(self):
        """Test error callback is called safely."""
        crawler = DocuCrawler("https://example.com")
        callback = Mock()
        crawler._on_error_callback = callback
        
        error = Exception("Test error")
        crawler._call_error_callback("https://example.com", error)
        
        callback.assert_called_once_with("https://example.com", error)
    
    def test_call_error_callback_none(self):
        """Test error callback when not set."""
        crawler = DocuCrawler("https://example.com")
        # should not raise
        crawler._call_error_callback("https://example.com", Exception("Test"))


if __name__ == '__main__':
    unittest.main()

