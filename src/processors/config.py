from dataclasses import dataclass
from typing import Optional, List
from urllib.parse import urlparse

@dataclass
class HtmlProcessorConfig:
    """
    Configuration for HTML to Markdown conversion.
    
    Provides comprehensive control over conversion behavior, similar to html2text
    but with additional documentation-specific options.
    """
    ignore_links: bool = False
    ignore_images: bool = False
    body_width: int = 0
    dash_unordered_list: bool = False
    skip_internal_links: bool = False
    escape_snob: bool = False
    unicode_snob: bool = True
    wrap_links: bool = True
    google_doc: bool = False
    hide_strikethrough: bool = False
    base_url: Optional[str] = None
    single_file: bool = False  # new option for consolidating output
    include_frontmatter: bool = False  # include YAML frontmatter
    
    def should_skip_link(self, href: str) -> bool:
        """Determine if a link should be skipped based on configuration."""
        if self.ignore_links:
            return True
        
        if self.skip_internal_links and self.base_url:
            try:
                link_domain = urlparse(href).netloc
                base_domain = urlparse(self.base_url).netloc
                if link_domain == base_domain or (not link_domain and href.startswith('/')):
                    return True
            except Exception:
                pass
        
        return False
    
    def wrap_text(self, text: str) -> str:
        """Wrap text to body_width if specified."""
        if self.body_width <= 0:
            return text
        
        lines = []
        for line in text.split('\n'):
            if len(line) <= self.body_width:
                lines.append(line)
            else:
                words = line.split()
                current_line = []
                current_length = 0
                
                for word in words:
                    word_length = len(word)
                    if current_length + word_length + 1 <= self.body_width:
                        if current_line:
                            current_line.append(' ')
                            current_length += 1
                        current_line.append(word)
                        current_length += word_length
                    else:
                        if current_line:
                            lines.append(''.join(current_line))
                        current_line = [word]
                        current_length = word_length
                
                if current_line:
                    lines.append(''.join(current_line))
        
        return '\n'.join(lines)

