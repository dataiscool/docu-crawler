"""Tests for URL utility functions."""
import unittest
from src.utils.url_utils import is_valid_url, url_to_filepath, should_add_to_queue, NON_HTML_EXTENSIONS
from collections import deque


class TestURLUtils(unittest.TestCase):
    """Test cases for URL utility functions."""
    
    def test_is_valid_url_same_domain(self):
        """Test URL validation with same domain."""
        self.assertTrue(is_valid_url(
            "https://example.com/docs/page",
            "example.com",
            "/docs"
        ))
    
    def test_is_valid_url_different_domain(self):
        """Test URL validation with different domain."""
        self.assertFalse(is_valid_url(
            "https://other.com/docs/page",
            "example.com",
            "/docs"
        ))
    
    def test_is_valid_url_outside_base_path(self):
        """Test URL validation outside base path."""
        self.assertFalse(is_valid_url(
            "https://example.com/other/page",
            "example.com",
            "/docs"
        ))
    
    def test_is_valid_url_non_html_extension(self):
        """Test URL validation with non-HTML extension."""
        for ext in NON_HTML_EXTENSIONS:
            self.assertFalse(is_valid_url(
                f"https://example.com/docs/image{ext}",
                "example.com",
                "/docs"
            ))
    
    def test_url_to_filepath_basic(self):
        """Test URL to filepath conversion."""
        result = url_to_filepath(
            "https://example.com/docs/page",
            "/docs",
            "output"
        )
        self.assertEqual(result, "page.md")
    
    def test_url_to_filepath_index(self):
        """Test URL to filepath conversion for index page."""
        result = url_to_filepath(
            "https://example.com/docs/",
            "/docs",
            "output"
        )
        self.assertEqual(result, "index.md")
    
    def test_url_to_filepath_nested(self):
        """Test URL to filepath conversion for nested path."""
        result = url_to_filepath(
            "https://example.com/docs/section/page",
            "/docs",
            "output"
        )
        self.assertEqual(result, "section/page.md")
    
    def test_should_add_to_queue_new_url(self):
        """Test should_add_to_queue with new URL."""
        visited = set()
        queue = deque(["https://example.com/page1"])
        
        self.assertTrue(should_add_to_queue(
            "https://example.com/page2",
            visited,
            queue
        ))
    
    def test_should_add_to_queue_already_visited(self):
        """Test should_add_to_queue with already visited URL."""
        visited = {"https://example.com/page1"}
        queue = deque()
        
        self.assertFalse(should_add_to_queue(
            "https://example.com/page1",
            visited,
            queue
        ))
    
    def test_should_add_to_queue_already_in_queue(self):
        """Test should_add_to_queue with URL already in queue."""
        visited = set()
        queue = deque(["https://example.com/page1"])
        
        self.assertFalse(should_add_to_queue(
            "https://example.com/page1",
            visited,
            queue
        ))


if __name__ == '__main__':
    unittest.main()

