import unittest
from src.processors.html_processor import HtmlProcessor
from src.processors.config import HtmlProcessorConfig

class TestHtmlProcessor(unittest.TestCase):
    """Test cases for HtmlProcessor."""

    def test_default_extraction(self):
        """Test basic text extraction with default config."""
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <main>
                    <h1>Hello World</h1>
                    <p>This is a test.</p>
                </main>
            </body>
        </html>
        """
        processor = HtmlProcessor()
        markdown = processor.extract_text(html)
        # content has H1, so title isn't prepended
        self.assertIn("# Hello World", markdown) 
        self.assertIn("This is a test.", markdown)

    def test_ignore_links(self):
        """Test ignoring links."""
        config = HtmlProcessorConfig(ignore_links=True)
        processor = HtmlProcessor(config)
        # wrap in main to ensure content detection works
        html = """
        <html>
            <head><title>Test</title></head>
            <body>
                <main>
                    <p>Check <a href='https://example.com'>this link</a>.</p>
                </main>
            </body>
        </html>
        """
        markdown = processor.extract_text(html)
        # whitespace handling might introduce space before punctuation
        self.assertIn("Check this link", markdown)
        self.assertNotIn("](https://example.com)", markdown)

    def test_ignore_images(self):
        """Test ignoring images."""
        config = HtmlProcessorConfig(ignore_images=True)
        processor = HtmlProcessor(config)
        # wrap in main to ensure content detection works
        html = """
        <html>
            <head><title>Test</title></head>
            <body>
                <main>
                    <p>Image: <img src='test.png' alt='Test'></p>
                </main>
            </body>
        </html>
        """
        markdown = processor.extract_text(html)
        self.assertIn("Image:", markdown)
        self.assertNotIn("![Test](test.png)", markdown)

    def test_post_process_cleanup(self):
        """Test post-processing cleanup of empty links and excessive newlines."""
        processor = HtmlProcessor()
        # markdown with empty links and too many newlines
        raw_markdown = "Text\n\n\n[]()\n\nMore Text"
        cleaned = processor._post_process_markdown(raw_markdown)
        self.assertNotIn("[]()", cleaned)
        self.assertNotIn("\n\n\n", cleaned)
        self.assertIn("\n\n", cleaned)

    def test_main_content_selection(self):
        """Test selection of main content via selectors."""
        html = """
        <html>
            <head><title>Selector Test</title></head>
            <body>
                <div id="sidebar">Sidebar</div>
                <div class="documentation">
                    <h1>Real Content</h1>
                </div>
                <footer>Footer</footer>
            </body>
        </html>
        """
        processor = HtmlProcessor()
        markdown = processor.extract_text(html)
        self.assertIn("Real Content", markdown)
        self.assertNotIn("Sidebar", markdown) # sidebar should be ignored if main content found
        self.assertNotIn("Footer", markdown) # footer is in ELEMENTS_TO_REMOVE

if __name__ == '__main__':
    unittest.main()
