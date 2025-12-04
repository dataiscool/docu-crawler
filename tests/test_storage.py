"""Tests for storage backends."""
import unittest
import tempfile
import os
from pathlib import Path
from src.utils.storage.local import LocalStorageBackend


class TestLocalStorageBackend(unittest.TestCase):
    """Test cases for LocalStorageBackend."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = LocalStorageBackend(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_file_string(self):
        """Test saving string content."""
        self.storage.save_file("test.md", "Test content")
        file_path = Path(self.temp_dir) / "test.md"
        self.assertTrue(file_path.exists())
        self.assertEqual(file_path.read_text(), "Test content")
    
    def test_save_file_bytes(self):
        """Test saving bytes content."""
        self.storage.save_file("test.bin", b"Test bytes")
        file_path = Path(self.temp_dir) / "test.bin"
        self.assertTrue(file_path.exists())
        self.assertEqual(file_path.read_bytes(), b"Test bytes")
    
    def test_save_file_nested_path(self):
        """Test saving file in nested directory."""
        self.storage.save_file("nested/path/test.md", "Content")
        file_path = Path(self.temp_dir) / "nested" / "path" / "test.md"
        self.assertTrue(file_path.exists())
    
    def test_exists(self):
        """Test file existence check."""
        self.storage.save_file("test.md", "Content")
        self.assertTrue(self.storage.exists("test.md"))
        self.assertFalse(self.storage.exists("nonexistent.md"))
    
    def test_get_file(self):
        """Test retrieving file content."""
        self.storage.save_file("test.md", "Content")
        content = self.storage.get_file("test.md")
        self.assertEqual(content, b"Content")
    
    def test_get_file_nonexistent(self):
        """Test retrieving nonexistent file."""
        content = self.storage.get_file("nonexistent.md")
        self.assertIsNone(content)
    
    def test_sanitize_path(self):
        """Test path sanitization."""
        # test directory traversal prevention
        safe_path = self.storage._sanitize_path("../../../etc/passwd")
        self.assertNotIn("..", str(safe_path))
        # After removing .. parts, remaining path should be sanitized
        # The .. parts are removed, leaving etc/passwd which is valid
        # But we should ensure it doesn't go outside the output directory
        path_str = str(safe_path)
        # Should not contain .. (directory traversal)
        self.assertNotIn("..", path_str)
        # Should be a relative path (not absolute)
        self.assertFalse(path_str.startswith('/'))
        self.assertFalse(path_str.startswith('\\'))

    def test_append_file(self):
        """Test appending content to a file."""
        self.storage.save_file("append.md", "Initial content")
        self.storage.append_file("append.md", "\nAppended content")
        
        content = self.storage.get_file("append.md")
        self.assertEqual(content.decode('utf-8'), "Initial content\nAppended content")
        
    def test_append_file_new(self):
        """Test appending to a non-existent file (should create it)."""
        self.storage.append_file("new_append.md", "Start content")
        content = self.storage.get_file("new_append.md")
        self.assertEqual(content.decode('utf-8'), "Start content")


if __name__ == '__main__':
    unittest.main()

