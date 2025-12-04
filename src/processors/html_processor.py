import re
from typing import List, Callable, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag, NavigableString
from urllib.parse import urljoin, urldefrag
import logging

from .config import HtmlProcessorConfig

logger = logging.getLogger('DocuCrawler')

class HtmlProcessor:
    """
    Handles HTML content processing and conversion to Markdown.
    
    Superior to html2text with:
    - Smart content extraction (documentation-focused)
    - Comprehensive configuration options
    - Better edge case handling
    - Zero additional dependencies
    """
    
    ELEMENTS_TO_REMOVE = [
        "script", "style", "iframe", "nav", "footer", "header", 
        "aside", "noscript", "meta", "button", "svg", "canvas",
        "[aria-hidden=true]", ".navigation", ".sidebar", ".menu", 
        ".ads", ".banner", ".cookie-notice", ".social-links"
    ]
    
    MARKDOWN_SUBSTITUTIONS = {
        'hr': '---',
        'br': '\n'
    }

    # Selectors for identifying the main content area
    MAIN_CONTENT_SELECTORS = [
        'main', 'article',
        'div.content', 'div.documentation', 'div.document',
        'div.docs-content', 'div.doc-content',
        'div#content', 'div#documentation', 'div#main-content', 'div#docs-content',
        'div.sphinx-content', 'div.md-content', 'div.page-inner',
        'div.markdown-section', 'div.section',
        'div.post-content', 'div.entry-content',
        'div[role="main"]'
    ]
    
    def __init__(self, config: Optional[HtmlProcessorConfig] = None):
        """
        Initialize HTML processor with optional configuration.
        
        Args:
            config: HtmlProcessorConfig instance for customization.
                   If None, uses default configuration.
        """
        self.config = config or HtmlProcessorConfig()
    
    def extract_text(self, html_content: str, url: str = '') -> str:
        """
        Extract content from HTML and convert it to Markdown format.
        
        Args:
            html_content: HTML content to parse
            url: URL of the page
            
        Returns:
            Extracted content in Markdown format
        """
        try:
            if self.config.base_url is None:
                self.config.base_url = url
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            if self.config.google_doc:
                self._process_google_doc(soup)
            
            for selector in HtmlProcessor.ELEMENTS_TO_REMOVE:
                for element in soup.select(selector):
                    element.decompose()
            
            # Find main content using defined selectors
            main_content = None
            
            # 1. Try explicit selectors first
            for selector in self.MAIN_CONTENT_SELECTORS:
                if '.' in selector:
                    tag, cls = selector.split('.', 1)
                    main_content = soup.find(tag, class_=cls)
                elif '#' in selector:
                    tag, id_ = selector.split('#', 1)
                    main_content = soup.find(tag, id=id_)
                elif '[' in selector:
                    # simplistic handling for role="main"
                    tag = selector.split('[')[0]
                    attr_part = selector.split('[')[1].rstrip(']')
                    try:
                        attr, val = attr_part.split('=', 1)
                        val = val.strip('"\'')
                        main_content = soup.find(tag, attrs={attr: val})
                    except ValueError:
                        # Invalid attribute selector format, skip
                        logger.debug(f"Invalid attribute selector format: {selector}")
                        continue
                else:
                    main_content = soup.find(selector)
                
                if main_content:
                    break
            
            # 2. Heuristic fallback: look for content/doc in class/id
            if not main_content:
                main_content = soup.find('div', class_=lambda c: c and ('content' in c.lower() or 'doc' in c.lower()))
            
            # 3. Ultimate fallback: use body
            if not main_content:
                main_content = soup.body
            
            if not main_content:
                title = soup.title.string.strip() if soup.title and soup.title.string else 'Untitled Page'
                return f"# {title}\n\nNo main content could be extracted from this page."
                
            content_copy = BeautifulSoup(str(main_content), 'html.parser')
            title = soup.title.string.strip() if soup.title and soup.title.string else 'Untitled Page'
            if ' | ' in title:
                title = title.split(' | ')[0].strip()
            elif ' - ' in title:
                title = title.split(' - ')[0].strip()
                
            markdown_content = self._convert_to_markdown(content_copy)
            
            if self.config.include_frontmatter:
                markdown_content = self._add_frontmatter(markdown_content, title, url)
            
            if not markdown_content.startswith('# ') and not self.config.include_frontmatter:
                markdown_content = f"# {title}\n\n{markdown_content}"
                
            markdown_content = self._post_process_markdown(markdown_content)
            
            if self.config.body_width > 0:
                markdown_content = self.config.wrap_text(markdown_content)
                
            return markdown_content
            
        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {str(e)}", exc_info=True)
            return self._simple_html_to_markdown(html_content)
    
    def _add_frontmatter(self, markdown: str, title: str, url: str) -> str:
        """
        Add YAML frontmatter to the markdown content.
        
        Args:
            markdown: Markdown content
            title: Page title
            url: Page URL
            
        Returns:
            Markdown with frontmatter prepended
        """
        import time
        date = time.strftime('%Y-%m-%d')
        
        frontmatter = [
            '---',
            f'title: "{title}"',
            f'source: "{url}"',
            f'date: {date}',
            '---',
            ''
        ]
        
        # If the content already starts with a title that matches, we might want to keep it or remove it.
        # Usually frontmatter replaces the H1 title, but let's keep H1 for now as it's part of the content.
        
        return '\n'.join(frontmatter) + markdown

    def _convert_to_markdown(self, soup: BeautifulSoup) -> str:
        """
        Recursively convert HTML content to Markdown with proper structure.
        
        Args:
            soup: BeautifulSoup object to convert
            
        Returns:
            Converted Markdown string
        """
        self._process_code(soup)
        self._process_tables(soup)
        self._process_lists(soup)
        self._process_blockquotes(soup)
        self._process_horizontal_rules(soup)
        self._process_headings(soup)
        if not self.config.ignore_images:
            self._process_images(soup)
        if not self.config.ignore_links:
            self._process_links(soup)
        self._process_text_formatting(soup)
        
        return self._build_markdown_from_tree(soup)
    
    def _build_markdown_from_tree(self, element) -> str:
        """
        Build markdown by traversing the element tree.
        
        Args:
            element: BeautifulSoup element or Tag
            
        Returns:
            Markdown string
        """
        if isinstance(element, NavigableString):
            text = str(element)
            text = re.sub(r'[ \t]+', ' ', text)
            return text
        
        if not hasattr(element, 'children'):
            return ''
        
        markdown_parts = []
        
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    markdown_parts.append(text)
            elif hasattr(child, 'name'):
                tag_name = child.name
                
                if tag_name in ['p', 'div', 'section', 'article', 'main']:
                    child_md = self._build_markdown_from_tree(child).strip()
                    if child_md:
                        markdown_parts.append(child_md)
                        markdown_parts.append('')
                
                elif tag_name and tag_name.startswith('h') and tag_name[1:].isdigit():
                    child_md = self._build_markdown_from_tree(child).strip()
                    if child_md:
                        markdown_parts.append(child_md)
                        markdown_parts.append('')
                
                elif tag_name in ['ul', 'ol', 'li']:
                    child_md = self._build_markdown_from_tree(child).strip()
                    if child_md:
                        markdown_parts.append(child_md)
                
                elif tag_name == 'br':
                    markdown_parts.append('\n')
                else:
                    child_md = self._build_markdown_from_tree(child).strip()
                    if child_md:
                        markdown_parts.append(child_md)
        
        result = ' '.join(markdown_parts)
        result = re.sub(r' +', ' ', result)
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result
    
    def _post_process_markdown(self, markdown: str) -> str:
        """
        Clean up the generated Markdown.
        
        Args:
            markdown: Raw markdown content
            
        Returns:
            Cleaned markdown content
        """
        # Remove empty links and images (useless tokens for LLMs)
        markdown = re.sub(r'\[\s*\]\([^)]*\)', '', markdown)
        markdown = re.sub(r'!\[\s*\]\([^)]*\)', '', markdown)
        
        # Consolidate excessive newlines (max 2)
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # Fix common list formatting issues
        markdown = re.sub(r'\n\*', '\n\n*', markdown)
        markdown = re.sub(r'\n\d+\.', '\n\n\\g<0>', markdown)
        
        # Ensure code blocks have proper spacing
        markdown = re.sub(r'```\s+', '```\n', markdown)
        markdown = re.sub(r'\s+```', '\n```', markdown)
        
        # Ensure headers have space after #
        markdown = re.sub(r'([^\n])(\n#{1,6} )', '\\1\n\n\\2', markdown)
        
        paragraphs = []
        current_paragraph = []
        
        for line in markdown.split('\n'):
            stripped = line.strip()
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
            
            if not stripped:
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                paragraphs.append('')
            elif is_special:
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                paragraphs.append(stripped)
            else:
                current_paragraph.append(stripped)
        
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        markdown = '\n\n'.join(p for p in paragraphs if p)
        markdown = markdown.strip()
        
        return markdown
    
    def _simple_html_to_markdown(self, html_content: str) -> str:
        """
        A simpler fallback HTML to Markdown conversion.
        
        Args:
            html_content: HTML content to convert
            
        Returns:
            Converted Markdown string
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for tag in soup(["script", "style"]):
                tag.decompose()
            
            title = soup.title.string.strip() if soup.title and soup.title.string else 'Untitled Page'
            text = soup.get_text('\n', strip=True)
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r' +', ' ', text)
            markdown = f"# {title}\n\n{text}"
            
            return markdown
        except Exception as e:
            logger.error(f"Error in simple HTML to Markdown conversion: {str(e)}")
            return "# Error Converting Page\n\nThere was an error converting this page to Markdown."
    
    def _process_headings(self, content):
        """Process HTML headings to Markdown format."""
        for i in range(1, 7):
            for heading in content.find_all(f'h{i}'):
                if heading.get('data-processed'):
                    continue
                heading_text = self._get_inline_text(heading).strip()
                if heading_text:
                    heading_md = '#' * i
                    heading.replace_with(NavigableString(f"{heading_md} {heading_text}"))
                    heading['data-processed'] = 'true'
    
    def _process_links(self, content):
        """Process HTML links to Markdown format."""
        for link in content.find_all('a', href=True):
            if link.get('data-processed'):
                continue
            
            href = link['href']
            if self.config.should_skip_link(href):
                link_text = self._get_inline_text(link).strip() or href
                link.replace_with(NavigableString(link_text))
                link['data-processed'] = 'true'
                continue
            
            link_text = self._get_inline_text(link).strip()
            if not link_text:
                link_text = href
            
            if self.config.escape_snob:
                link_text = link_text.replace('[', '\\[').replace(']', '\\]')
                href = href.replace('(', '\\(').replace(')', '\\)')
            else:
                link_text = link_text.replace('[', '\\[').replace(']', '\\]')
            
            if self.config.wrap_links and len(href) > 50:
                link_md = f"[{link_text}]({href})"
            else:
                link_md = f"[{link_text}]({href})"
            
            link.replace_with(NavigableString(link_md))
            link['data-processed'] = 'true'
    
    def _process_images(self, content):
        """Process HTML images to Markdown format."""
        for img in content.find_all('img', src=True):
            if img.get('data-processed'):
                continue
            alt_text = img.get('alt', '').strip() or img.get('title', '').strip() or 'Image'
            src = img['src']
            
            if self.config.escape_snob:
                alt_text = alt_text.replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)')
            else:
                alt_text = alt_text.replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)')
            
            img.replace_with(NavigableString(f"![{alt_text}]({src})"))
            img['data-processed'] = 'true'
    
    def _process_code(self, content):
        """Process HTML code blocks and inline code to Markdown format."""
        for pre in content.find_all('pre'):
            if pre.get('data-processed'):
                continue
            
            code_element = pre.find('code')
            if code_element:
                language = ''
                if code_element.get('class'):
                    for cls in code_element.get('class'):
                        if cls.startswith(('language-', 'lang-', 'highlight-')):
                            parts = cls.split('-', 1)
                            if len(parts) > 1:
                                language = parts[1]
                            break
                        elif cls.startswith('brush:'):
                            language = cls.split(':', 1)[1] if ':' in cls else ''
                            break
                
                if not language and pre.get('class'):
                    for cls in pre.get('class'):
                        if cls.startswith(('language-', 'lang-', 'highlight-')):
                            parts = cls.split('-', 1)
                            if len(parts) > 1:
                                language = parts[1]
                            break
                        elif cls.startswith('brush:'):
                            language = cls.split(':', 1)[1] if ':' in cls else ''
                            break
                
                code_text = code_element.get_text()
                pre.replace_with(NavigableString(f"\n```{language}\n{code_text}\n```\n"))
                pre['data-processed'] = 'true'
            else:
                code_text = pre.get_text()
                pre.replace_with(NavigableString(f"\n```\n{code_text}\n```\n"))
                pre['data-processed'] = 'true'
        
        for code in content.find_all('code'):
            if code.parent and code.parent.name == 'pre':
                continue
            if code.get('data-processed'):
                continue
            
            code_text = code.get_text()
            if self.config.escape_snob:
                code_text = code_text.replace('`', '\\`').replace('*', '\\*').replace('_', '\\_')
            else:
                code_text = code_text.replace('`', '\\`')
            code.replace_with(NavigableString(f"`{code_text}`"))
            code['data-processed'] = 'true'
    
    def _process_text_formatting(self, content):
        """Process HTML text formatting to Markdown format."""
        for em in content.find_all(['em', 'i']):
            if em.get('data-processed'):
                continue
            em_text = self._get_inline_text(em).strip()
            if em_text:
                em.replace_with(NavigableString(f"*{em_text}*"))
                em['data-processed'] = 'true'
        
        for strong in content.find_all(['strong', 'b']):
            if strong.get('data-processed'):
                continue
            strong_text = self._get_inline_text(strong).strip()
            if strong_text:
                strong.replace_with(NavigableString(f"**{strong_text}**"))
                strong['data-processed'] = 'true'

        if not self.config.hide_strikethrough:
            for s in content.find_all(['s', 'strike', 'del']):
                if s.get('data-processed'):
                    continue
                s_text = self._get_inline_text(s).strip()
                if s_text:
                    s.replace_with(NavigableString(f"~~{s_text}~~"))
                    s['data-processed'] = 'true'
    
    def _get_inline_text(self, element) -> str:
        """
        Get text content from an element, preserving inline formatting.
        This is used for elements that should preserve their children's formatting.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Text content with formatting preserved
        """
        if isinstance(element, NavigableString):
            return str(element)
        
        parts = []
        for child in element.children:
            if isinstance(child, NavigableString):
                parts.append(str(child))
            elif hasattr(child, 'name'):
                parts.append(self._get_inline_text(child))
        
        return ''.join(parts)
    
    def _process_lists(self, content):
        """Process HTML lists to Markdown format with proper nesting."""
        for list_tag in content.find_all(['ul', 'ol']):
            if list_tag.get('data-processed'):
                continue
            
            list_items = []

            if list_tag.name == 'ol':
                start = list_tag.get('start', 1)
                try:
                    start = int(start)
                except (ValueError, TypeError):
                    start = 1
                
                for i, li in enumerate(list_tag.find_all('li', recursive=False), start):
                    li_content = self._process_list_item(li)
                    if li_content.strip():
                        list_items.append(f"{i}. {li_content}")

            elif list_tag.name == 'ul':
                marker = '-' if self.config.dash_unordered_list else '*'
                for li in list_tag.find_all('li', recursive=False):
                    li_content = self._process_list_item(li)
                    if li_content.strip():
                        list_items.append(f"{marker} {li_content}")

            if list_items:
                list_markdown = '\n'.join(list_items)
                list_tag.replace_with(NavigableString(f"\n{list_markdown}\n"))
                list_tag['data-processed'] = 'true'
    
    def _process_list_item(self, li) -> str:
        """
        Process a single list item, handling nested content.
        
        Args:
            li: BeautifulSoup li element
            
        Returns:
            Markdown representation of the list item
        """
        parts = []
        
        for child in li.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    parts.append(text)
            elif hasattr(child, 'name'):
                tag_name = child.name
                
                if tag_name in ['ul', 'ol']:
                    self._process_lists(child)
                    nested_md = self._build_markdown_from_tree(child).strip()
                    if nested_md:
                        indented = '\n'.join('  ' + line if line.strip() else line 
                                           for line in nested_md.split('\n'))
                        parts.append(indented)
                else:
                    child_md = self._build_markdown_from_tree(child).strip()
                    if child_md:
                        parts.append(child_md)
        
        return ' '.join(parts).strip()
    
    def _process_tables(self, content):
        """Process HTML tables to Markdown format."""
        for table in content.find_all('table'):
            if table.get('data-processed'):
                continue
            
            markdown_table = []
            
            if table.find('thead'):
                header_cells = table.find('thead').find_all('th')
                if header_cells:
                    cell_texts = []
                    for cell in header_cells:
                        cell_text = self._build_markdown_from_tree(cell).strip()
                        cell_text = cell_text.replace('|', '\\|').replace('\n', ' ')
                        cell_texts.append(cell_text)
                    header_row = '| ' + ' | '.join(cell_texts) + ' |'
                    separator_row = '| ' + ' | '.join(['---'] * len(header_cells)) + ' |'
                    markdown_table.append(header_row)
                    markdown_table.append(separator_row)

            if table.find('tbody'):
                tbody = table.find('tbody')
                header_cols = len(header_cells) if header_cells else None
                for row in tbody.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if not cells:
                        continue
                    
                    cell_texts = []
                    for cell in cells:
                        cell_text = self._build_markdown_from_tree(cell).strip()
                        cell_text = cell_text.replace('|', '\\|').replace('\n', ' ')
                        cell_texts.append(cell_text)
                    
                    if header_cols and len(cell_texts) != header_cols:
                        cell_texts.extend([''] * (header_cols - len(cell_texts)))
                    
                    row_text = '| ' + ' | '.join(cell_texts) + ' |'
                    markdown_table.append(row_text)

            if not markdown_table:
                rows = table.find_all('tr')
                has_header = False
                first_row_cells = None
                
                for i, row in enumerate(rows):
                    cells = row.find_all(['td', 'th'])
                    if not cells:
                        continue
                    
                    if first_row_cells is None:
                        first_row_cells = cells
                    
                    cell_texts = []
                    for cell in cells:
                        cell_text = self._build_markdown_from_tree(cell).strip()
                        cell_text = cell_text.replace('|', '\\|').replace('\n', ' ')
                        cell_texts.append(cell_text)
                    
                    row_text = '| ' + ' | '.join(cell_texts) + ' |'
                    markdown_table.append(row_text)
                    
                    if i == 0 and any(cell.name == 'th' for cell in cells) and not has_header:
                        separator_row = '| ' + ' | '.join(['---'] * len(cells)) + ' |'
                        markdown_table.insert(1, separator_row)
                        has_header = True
                    
                    if not has_header and i == 0 and first_row_cells:
                        num_cols = len(first_row_cells)
                        if len(markdown_table) > 0:
                            separator_row = '| ' + ' | '.join(['---'] * num_cols) + ' |'
                            markdown_table.insert(1, separator_row)
                            has_header = True
            
            if markdown_table:
                table.replace_with(NavigableString('\n' + '\n'.join(markdown_table) + '\n'))
                table['data-processed'] = 'true'
    
    def _process_blockquotes(self, content):
        """Process HTML blockquotes to Markdown format."""
        for blockquote in content.find_all('blockquote'):
            if blockquote.get('data-processed'):
                continue

            quote_content = self._build_markdown_from_tree(blockquote).strip()

            formatted_quote = '\n'.join(f"> {line}" if line.strip() else ">" 
                                       for line in quote_content.split('\n'))
            
            blockquote.replace_with(NavigableString(f"\n{formatted_quote}\n"))
            blockquote['data-processed'] = 'true'
    
    def _process_horizontal_rules(self, content):
        """Process HTML horizontal rules to Markdown format."""
        for hr in content.find_all('hr'):
            if hr.get('data-processed'):
                continue
            hr.replace_with(NavigableString("\n---\n"))
            hr['data-processed'] = 'true'
    
    def _process_google_doc(self, soup):
        """Process Google Docs specific HTML formatting."""
        for span in soup.find_all('span', style=True):
            style = span.get('style', '')
            if 'text-decoration:line-through' in style and self.config.hide_strikethrough:
                span.decompose()
            elif 'font-weight:700' in style or 'font-weight:bold' in style:
                if span.name != 'strong' and span.name != 'b':
                    strong = soup.new_tag('strong')
                    strong.string = span.get_text()
                    span.replace_with(strong)
            elif 'font-style:italic' in style:
                if span.name != 'em' and span.name != 'i':
                    em = soup.new_tag('em')
                    em.string = span.get_text()
                    span.replace_with(em)
    
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

            if (href.startswith('#') or 
                href.startswith('javascript:') or 
                href.startswith('mailto:') or
                href.startswith('tel:')):
                continue

            absolute_url = urljoin(current_url, href)
            
            # Remove fragment (anchor) to avoid duplicate crawling of same page
            absolute_url, _ = urldefrag(absolute_url)

            if is_valid_url_func(absolute_url):
                links.append(absolute_url)
                
        return links
    
    @staticmethod
    def extract_text_static(html_content: str, url: str = '', config: Optional[HtmlProcessorConfig] = None) -> str:
        """
        Static method for backward compatibility.
        
        Args:
            html_content: HTML content to parse
            url: URL of the page
            config: Optional configuration (creates default if None)
            
        Returns:
            Extracted content in Markdown format
        """
        processor = HtmlProcessor(config)
        return processor.extract_text(html_content, url)