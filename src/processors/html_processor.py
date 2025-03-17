import re
from typing import List, Callable, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag, NavigableString
from urllib.parse import urljoin
import logging

logger = logging.getLogger('DocCrawler')

class HtmlProcessor:
    """Handles HTML content processing and conversion to Markdown."""
    
    # Common HTML elements to remove that don't contribute to content
    ELEMENTS_TO_REMOVE = [
        "script", "style", "iframe", "nav", "footer", "header", 
        "aside", "noscript", "meta", "button", "svg", "canvas",
        "[aria-hidden=true]", ".navigation", ".sidebar", ".menu", 
        ".ads", ".banner", ".cookie-notice", ".social-links"
    ]
    
    # Map HTML elements to their Markdown counterparts for simple replacements
    MARKDOWN_SUBSTITUTIONS = {
        'hr': '---',
        'br': '\n'
    }
    
    @staticmethod
    def extract_text(html_content: str) -> str:
        """
        Extract content from HTML and convert it to Markdown format.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Extracted content in Markdown format
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unnecessary elements
            for selector in HtmlProcessor.ELEMENTS_TO_REMOVE:
                for element in soup.select(selector):
                    element.decompose()
            
            # Get the main content with exhaustive selectors for different documentation formats
            main_content = (
                # Common documentation containers
                soup.find('main') or 
                soup.find('article') or 
                
                # Documentation-specific selectors
                soup.find('div', class_='content') or 
                soup.find('div', class_='documentation') or
                soup.find('div', class_='document') or
                soup.find('div', class_='docs-content') or
                soup.find('div', class_='doc-content') or
                soup.find('div', id='content') or
                soup.find('div', id='documentation') or
                soup.find('div', id='main-content') or
                soup.find('div', id='docs-content') or
                
                # Framework-specific documentation selectors
                soup.find('div', class_='sphinx-content') or
                soup.find('div', class_='md-content') or
                soup.find('div', class_='page-inner') or
                soup.find('div', class_='markdown-section') or
                soup.find('div', class_='section') or
                soup.find('div', class_='post-content') or
                
                # Fallbacks for other documentation systems
                soup.find('div', class_='container') or
                soup.find('div', class_='wrapper') or
                soup.find('div', class_='entry-content') or
                soup.find('div', role='main') or
                
                # Final fallbacks if nothing specific is found
                soup.find('div', class_=lambda c: c and ('content' in c.lower() or 'doc' in c.lower())) or
                soup.body
            )
            
            if not main_content:
                # If no main content is found, return the title as a fallback
                title = soup.title.string.strip() if soup.title else 'Untitled Page'
                return f"# {title}\n\nNo main content could be extracted from this page."
                
            # Create a working copy to avoid modifying the original during processing
            content_copy = BeautifulSoup(str(main_content), 'html.parser')
            
            # Extract the page title
            title = soup.title.string.strip() if soup.title else 'Untitled Page'
            # Clean up title (remove site name if present)
            if ' | ' in title:
                title = title.split(' | ')[0].strip()
            elif ' - ' in title:
                title = title.split(' - ')[0].strip()
                
            # Convert the HTML to a structured Markdown document
            markdown_content = HtmlProcessor._convert_to_markdown(content_copy)
            
            # Add title as H1 if there's no H1 already in the document
            if not markdown_content.startswith('# '):
                markdown_content = f"# {title}\n\n{markdown_content}"
                
            # Final cleanup
            markdown_content = HtmlProcessor._post_process_markdown(markdown_content)
                
            return markdown_content
            
        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {str(e)}", exc_info=True)
            # Fallback to a simpler conversion
            return HtmlProcessor._simple_html_to_markdown(html_content)
    
    @staticmethod
    def _convert_to_markdown(soup: BeautifulSoup) -> str:
        """
        Recursively convert HTML content to Markdown with proper structure.
        
        Args:
            soup: BeautifulSoup object to convert
            
        Returns:
            Converted Markdown string
        """
        # Process elements that need special handling
        HtmlProcessor._process_headings(soup)
        HtmlProcessor._process_links(soup)
        HtmlProcessor._process_images(soup)
        HtmlProcessor._process_code(soup)
        HtmlProcessor._process_text_formatting(soup)
        HtmlProcessor._process_lists(soup)
        HtmlProcessor._process_tables(soup)
        HtmlProcessor._process_blockquotes(soup)
        HtmlProcessor._process_horizontal_rules(soup)
        
        # Convert to text
        text = soup.get_text(' ', strip=True)
        
        # Replace multiple spaces with a single space
        text = re.sub(r' +', ' ', text)
        
        return text
    
    @staticmethod
    def _post_process_markdown(markdown: str) -> str:
        """
        Clean up the generated Markdown.
        
        Args:
            markdown: Raw markdown content
            
        Returns:
            Cleaned markdown content
        """
        # Replace multiple consecutive line breaks with double line breaks
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # Fix list items that might have been broken
        markdown = re.sub(r'\n\*', '\n\n*', markdown)
        markdown = re.sub(r'\n\d+\.', '\n\n\\g<0>', markdown)
        
        # Fix code blocks that might have incorrect spacing
        markdown = re.sub(r'```\s+', '```\n', markdown)
        markdown = re.sub(r'\s+```', '\n```', markdown)
        
        # Ensure headers have proper spacing
        markdown = re.sub(r'([^\n])(\n#{1,6} )', '\\1\n\n\\2', markdown)
        
        # Ensure paragraphs have proper spacing
        paragraphs = []
        current_paragraph = []
        
        for line in markdown.split('\n'):
            stripped = line.strip()
            
            # Check if line is a header, list item, code block, or other special element
            is_special = (
                stripped.startswith('#') or 
                stripped.startswith('* ') or 
                stripped.startswith('- ') or 
                stripped.startswith('+ ') or 
                stripped.startswith('1. ') or
                stripped.startswith('```') or
                stripped.startswith('|') or
                stripped.startswith('> ') or
                stripped == '---'
            )
            
            if not stripped:  # Empty line
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                paragraphs.append('')
            elif is_special:  # Special Markdown element
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                paragraphs.append(stripped)
            else:  # Regular paragraph text
                current_paragraph.append(stripped)
        
        # Add any remaining paragraph
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        # Join paragraphs with proper spacing
        markdown = '\n\n'.join(p for p in paragraphs if p)
        
        # Final cleanups
        markdown = markdown.strip()
        
        return markdown
    
    @staticmethod
    def _simple_html_to_markdown(html_content: str) -> str:
        """
        A simpler fallback HTML to Markdown conversion.
        
        Args:
            html_content: HTML content to convert
            
        Returns:
            Converted Markdown string
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for tag in soup(["script", "style"]):
                tag.decompose()
            
            # Get the title
            title = soup.title.string.strip() if soup.title else 'Untitled Page'
            
            # Extract text
            text = soup.get_text('\n', strip=True)
            
            # Clean up the text
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r' +', ' ', text)
            
            # Add the title as a header
            markdown = f"# {title}\n\n{text}"
            
            return markdown
        except Exception as e:
            logger.error(f"Error in simple HTML to Markdown conversion: {str(e)}")
            return "# Error Converting Page\n\nThere was an error converting this page to Markdown."
    
    @staticmethod
    def _process_headings(content):
        """Process HTML headings to Markdown format."""
        for i in range(1, 7):
            for heading in content.find_all(f'h{i}'):
                heading_text = heading.get_text().strip()
                heading_md = '#' * i
                heading.replace_with(f"{heading_md} {heading_text}")
    
    @staticmethod
    def _process_links(content):
        """Process HTML links to Markdown format."""
        for link in content.find_all('a', href=True):
            link_text = link.get_text().strip()
            # Skip empty links or links with no text
            if not link_text:
                continue
                
            href = link['href']
            link.replace_with(f"[{link_text}]({href})")
    
    @staticmethod
    def _process_images(content):
        """Process HTML images to Markdown format."""
        for img in content.find_all('img', src=True):
            alt_text = img.get('alt', '').strip() or img.get('title', '').strip() or 'Image'
            src = img['src']
            img.replace_with(f"![{alt_text}]({src})")
    
    @staticmethod
    def _process_code(content):
        """Process HTML code blocks and inline code to Markdown format."""
        # Process code blocks with language detection
        for pre in content.find_all('pre'):
            # Try to find the code element inside pre
            code_element = pre.find('code')
            if code_element:
                # Try to determine the language
                language = ''
                # Check class on code element
                if code_element.get('class'):
                    for cls in code_element.get('class'):
                        if cls.startswith(('language-', 'lang-')):
                            language = cls.split('-', 1)[1]
                            break
                
                # If no language found on code element, check pre
                if not language and pre.get('class'):
                    for cls in pre.get('class'):
                        if cls.startswith(('language-', 'lang-')):
                            language = cls.split('-', 1)[1]
                            break
                
                # Get the text from the code element
                code_text = code_element.get_text()
                # Replace the entire pre element
                pre.replace_with(f"```{language}\n{code_text}\n```")
            else:
                # If no code element found, use the pre content directly
                code_text = pre.get_text()
                pre.replace_with(f"```\n{code_text}\n```")
        
        # Process inline code
        for code in content.find_all('code'):
            # Skip if it's inside a pre (already processed)
            if code.parent.name != 'pre':
                code_text = code.get_text()
                code.replace_with(f"`{code_text}`")
    
    @staticmethod
    def _process_text_formatting(content):
        """Process HTML text formatting to Markdown format."""
        # Process emphasis (italic)
        for em in content.find_all(['em', 'i']):
            em_text = em.get_text()
            if em_text.strip():  # Only process if there's actual text
                em.replace_with(f"*{em_text}*")
        
        # Process strong (bold)
        for strong in content.find_all(['strong', 'b']):
            strong_text = strong.get_text()
            if strong_text.strip():  # Only process if there's actual text
                strong.replace_with(f"**{strong_text}**")
        
        # Process strikethrough
        for s in content.find_all(['s', 'strike', 'del']):
            s_text = s.get_text()
            if s_text.strip():  # Only process if there's actual text
                s.replace_with(f"~~{s_text}~~")
    
    @staticmethod
    def _process_lists(content):
        """Process HTML lists to Markdown format with proper nesting."""
        # First process all lists to add markers
        for list_tag in content.find_all(['ul', 'ol']):
            # Mark this list for processing
            list_tag['data-markdown-list'] = 'true'
            
            # Process ordered lists
            if list_tag.name == 'ol':
                start = list_tag.get('start', 1)
                try:
                    start = int(start)
                except (ValueError, TypeError):
                    start = 1
                
                for i, li in enumerate(list_tag.find_all('li', recursive=False), start):
                    li_text = li.get_text().strip()
                    # Don't process nested lists yet
                    has_nested = li.find(['ul', 'ol'])
                    if not has_nested and li_text:
                        li.replace_with(f"{i}. {li_text}")
            
            # Process unordered lists
            elif list_tag.name == 'ul':
                for li in list_tag.find_all('li', recursive=False):
                    li_text = li.get_text().strip()
                    # Don't process nested lists yet
                    has_nested = li.find(['ul', 'ol'])
                    if not has_nested and li_text:
                        li.replace_with(f"* {li_text}")
        
        # Now process and remove all list containers
        for list_tag in content.find_all(attrs={'data-markdown-list': 'true'}):
            # Get the text content with proper line breaks
            list_text = list_tag.get_text('\n')
            list_tag.replace_with(list_text)
    
    @staticmethod
    def _process_tables(content):
        """Process HTML tables to Markdown format."""
        for table in content.find_all('table'):
            markdown_table = []
            
            # Process header rows
            if table.find('thead'):
                header_cells = table.find('thead').find_all('th')
                if header_cells:
                    header_row = '| ' + ' | '.join(cell.get_text().strip() for cell in header_cells) + ' |'
                    separator_row = '| ' + ' | '.join(['---'] * len(header_cells)) + ' |'
                    markdown_table.append(header_row)
                    markdown_table.append(separator_row)
            
            # Process body rows
            if table.find('tbody'):
                for row in table.find('tbody').find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        # Escape pipe characters in cell content
                        cell_contents = [cell.get_text().strip().replace('|', '\\|') for cell in cells]
                        row_text = '| ' + ' | '.join(cell_contents) + ' |'
                        markdown_table.append(row_text)
            
            # If no tbody/thead structure, process all rows
            if not markdown_table:
                rows = table.find_all('tr')
                has_header = False
                
                for i, row in enumerate(rows):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        # Escape pipe characters in cell content
                        cell_contents = [cell.get_text().strip().replace('|', '\\|') for cell in cells]
                        row_text = '| ' + ' | '.join(cell_contents) + ' |'
                        markdown_table.append(row_text)
                        
                        # If this is the first row and contains th cells, add a separator
                        if i == 0 and row.find('th') and not has_header:
                            separator_row = '| ' + ' | '.join(['---'] * len(cells)) + ' |'
                            markdown_table.insert(1, separator_row)
                            has_header = True
            
            if markdown_table:
                table.replace_with('\n' + '\n'.join(markdown_table) + '\n')
    
    @staticmethod
    def _process_blockquotes(content):
        """Process HTML blockquotes to Markdown format."""
        for blockquote in content.find_all('blockquote'):
            # Get the text content
            quote_text = blockquote.get_text().strip()
            
            # Format as Markdown blockquote, adding > to each line
            formatted_quote = '\n'.join(f"> {line}" for line in quote_text.split('\n'))
            
            blockquote.replace_with(formatted_quote)
    
    @staticmethod
    def _process_horizontal_rules(content):
        """Process HTML horizontal rules to Markdown format."""
        for hr in content.find_all('hr'):
            hr.replace_with("\n---\n")
    
    @staticmethod
    def extract_links(html_content: str, current_url: str, is_valid_url_func: Callable[[str], bool]) -> List[str]:
        """
        Extract links from HTML content.
        
        Args:
            html_content: HTML content to parse
            current_url: Current URL for resolving relative URLs
            is_valid_url_func: Function to check if a URL is valid
            
        Returns:
            List of extracted URLs
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip anchor links, javascript, and mailto links
            if (href.startswith('#') or 
                href.startswith('javascript:') or 
                href.startswith('mailto:') or
                href.startswith('tel:')):
                continue
                
            # Resolve relative URLs
            absolute_url = urljoin(current_url, href)
            
            # Only add if the URL is valid and not already visited
            if is_valid_url_func(absolute_url):
                links.append(absolute_url)
                
        return links