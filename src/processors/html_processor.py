import re
from typing import List, Callable, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag, NavigableString
from urllib.parse import urljoin
import logging

logger = logging.getLogger('DocuCrawler')

class HtmlProcessor:
    """Handles HTML content processing and conversion to Markdown."""
    
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
    
    @staticmethod
    def extract_text(html_content: str, url: str = '') -> str:
        """
        Extract content from HTML and convert it to Markdown format.
        
        Args:
            html_content: HTML content to parse
            url: URL of the page
            
        Returns:
            Extracted content in Markdown format
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for selector in HtmlProcessor.ELEMENTS_TO_REMOVE:
                for element in soup.select(selector):
                    element.decompose()
            
            main_content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', class_='content') or 
                soup.find('div', class_='documentation') or
                soup.find('div', class_='document') or
                soup.find('div', class_='docs-content') or
                soup.find('div', class_='doc-content') or
                soup.find('div', id='content') or
                soup.find('div', id='documentation') or
                soup.find('div', id='main-content') or
                soup.find('div', id='docs-content') or
                soup.find('div', class_='sphinx-content') or
                soup.find('div', class_='md-content') or
                soup.find('div', class_='page-inner') or
                soup.find('div', class_='markdown-section') or
                soup.find('div', class_='section') or
                soup.find('div', class_='post-content') or
                soup.find('div', class_='container') or
                soup.find('div', class_='wrapper') or
                soup.find('div', class_='entry-content') or
                soup.find('div', role='main') or
                soup.find('div', class_=lambda c: c and ('content' in c.lower() or 'doc' in c.lower())) or
                soup.body
            )
            
            if not main_content:
                title = soup.title.string.strip() if soup.title else 'Untitled Page'
                return f"# {title}\n\nNo main content could be extracted from this page."
                
            content_copy = BeautifulSoup(str(main_content), 'html.parser')
            title = soup.title.string.strip() if soup.title else 'Untitled Page'
            if ' | ' in title:
                title = title.split(' | ')[0].strip()
            elif ' - ' in title:
                title = title.split(' - ')[0].strip()
                
            markdown_content = HtmlProcessor._convert_to_markdown(content_copy)
            
            if not markdown_content.startswith('# '):
                markdown_content = f"# {title}\n\n{markdown_content}"
                
            markdown_content = HtmlProcessor._post_process_markdown(markdown_content)
                
            return markdown_content
            
        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {str(e)}", exc_info=True)
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
        HtmlProcessor._process_code(soup)
        HtmlProcessor._process_tables(soup)
        HtmlProcessor._process_lists(soup)
        HtmlProcessor._process_blockquotes(soup)
        HtmlProcessor._process_horizontal_rules(soup)
        HtmlProcessor._process_headings(soup)
        HtmlProcessor._process_images(soup)
        HtmlProcessor._process_links(soup)
        HtmlProcessor._process_text_formatting(soup)
        
        return HtmlProcessor._build_markdown_from_tree(soup)
    
    @staticmethod
    def _build_markdown_from_tree(element) -> str:
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
                    child_md = HtmlProcessor._build_markdown_from_tree(child).strip()
                    if child_md:
                        markdown_parts.append(child_md)
                        markdown_parts.append('')
                
                elif tag_name and tag_name.startswith('h') and tag_name[1:].isdigit():
                    child_md = HtmlProcessor._build_markdown_from_tree(child).strip()
                    if child_md:
                        markdown_parts.append(child_md)
                        markdown_parts.append('')
                
                elif tag_name in ['ul', 'ol', 'li']:
                    child_md = HtmlProcessor._build_markdown_from_tree(child).strip()
                    if child_md:
                        markdown_parts.append(child_md)
                
                elif tag_name == 'br':
                    markdown_parts.append('\n')
                else:
                    child_md = HtmlProcessor._build_markdown_from_tree(child).strip()
                    if child_md:
                        markdown_parts.append(child_md)
        
        result = ' '.join(markdown_parts)
        result = re.sub(r' +', ' ', result)
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result
    
    @staticmethod
    def _post_process_markdown(markdown: str) -> str:
        """
        Clean up the generated Markdown.
        
        Args:
            markdown: Raw markdown content
            
        Returns:
            Cleaned markdown content
        """
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        markdown = re.sub(r'\n\*', '\n\n*', markdown)
        markdown = re.sub(r'\n\d+\.', '\n\n\\g<0>', markdown)
        markdown = re.sub(r'```\s+', '```\n', markdown)
        markdown = re.sub(r'\s+```', '\n```', markdown)
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
            
            for tag in soup(["script", "style"]):
                tag.decompose()
            
            title = soup.title.string.strip() if soup.title else 'Untitled Page'
            text = soup.get_text('\n', strip=True)
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r' +', ' ', text)
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
                heading_text = HtmlProcessor._get_inline_text(heading).strip()
                heading_md = '#' * i
                heading.replace_with(NavigableString(f"{heading_md} {heading_text}"))
    
    @staticmethod
    def _process_links(content):
        """Process HTML links to Markdown format."""
        for link in content.find_all('a', href=True):
            link_text = HtmlProcessor._get_inline_text(link).strip()
            if not link_text:
                continue
                
            href = link['href']
            link_text = link_text.replace('[', '\\[').replace(']', '\\]')
            link.replace_with(NavigableString(f"[{link_text}]({href})"))
    
    @staticmethod
    def _process_images(content):
        """Process HTML images to Markdown format."""
        for img in content.find_all('img', src=True):
            alt_text = img.get('alt', '').strip() or img.get('title', '').strip() or 'Image'
            src = img['src']
            alt_text = alt_text.replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)')
            img.replace_with(NavigableString(f"![{alt_text}]({src})"))
    
    @staticmethod
    def _process_code(content):
        """Process HTML code blocks and inline code to Markdown format."""
        for pre in content.find_all('pre'):
            if pre.get('data-processed'):
                continue
            
            code_element = pre.find('code')
            if code_element:
                language = ''
                if code_element.get('class'):
                    for cls in code_element.get('class'):
                        if cls.startswith(('language-', 'lang-')):
                            language = cls.split('-', 1)[1]
                            break
                
                if not language and pre.get('class'):
                    for cls in pre.get('class'):
                        if cls.startswith(('language-', 'lang-')):
                            language = cls.split('-', 1)[1]
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
            code_text = code_text.replace('`', '\\`')
            code.replace_with(NavigableString(f"`{code_text}`"))
            code['data-processed'] = 'true'
    
    @staticmethod
    def _process_text_formatting(content):
        """Process HTML text formatting to Markdown format."""
        for em in content.find_all(['em', 'i']):
            if em.get('data-processed'):
                continue
            em_text = HtmlProcessor._get_inline_text(em).strip()
            if em_text:
                em.replace_with(NavigableString(f"*{em_text}*"))
                em['data-processed'] = 'true'
        
        for strong in content.find_all(['strong', 'b']):
            if strong.get('data-processed'):
                continue
            strong_text = HtmlProcessor._get_inline_text(strong).strip()
            if strong_text:
                strong.replace_with(NavigableString(f"**{strong_text}**"))
                strong['data-processed'] = 'true'

        for s in content.find_all(['s', 'strike', 'del']):
            if s.get('data-processed'):
                continue
            s_text = HtmlProcessor._get_inline_text(s).strip()
            if s_text:
                s.replace_with(NavigableString(f"~~{s_text}~~"))
                s['data-processed'] = 'true'
    
    @staticmethod
    def _get_inline_text(element) -> str:
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
                parts.append(HtmlProcessor._get_inline_text(child))
        
        return ''.join(parts)
    
    @staticmethod
    def _process_lists(content):
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
                    li_content = HtmlProcessor._process_list_item(li)
                    if li_content.strip():
                        list_items.append(f"{i}. {li_content}")

            elif list_tag.name == 'ul':
                for li in list_tag.find_all('li', recursive=False):
                    li_content = HtmlProcessor._process_list_item(li)
                    if li_content.strip():
                        list_items.append(f"* {li_content}")

            if list_items:
                list_markdown = '\n'.join(list_items)
                list_tag.replace_with(NavigableString(f"\n{list_markdown}\n"))
                list_tag['data-processed'] = 'true'
    
    @staticmethod
    def _process_list_item(li) -> str:
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
                    HtmlProcessor._process_lists(child.parent)
                    nested_md = HtmlProcessor._build_markdown_from_tree(child).strip()
                    if nested_md:
                        indented = '\n'.join('  ' + line if line.strip() else line 
                                           for line in nested_md.split('\n'))
                        parts.append(indented)
                else:
                    child_md = HtmlProcessor._build_markdown_from_tree(child).strip()
                    if child_md:
                        parts.append(child_md)
        
        return ' '.join(parts).strip()
    
    @staticmethod
    def _process_tables(content):
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
                        cell_text = HtmlProcessor._build_markdown_from_tree(cell).strip()
                        cell_text = cell_text.replace('|', '\\|').replace('\n', ' ')
                        cell_texts.append(cell_text)
                    header_row = '| ' + ' | '.join(cell_texts) + ' |'
                    separator_row = '| ' + ' | '.join(['---'] * len(header_cells)) + ' |'
                    markdown_table.append(header_row)
                    markdown_table.append(separator_row)

            if table.find('tbody'):
                for row in table.find('tbody').find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        cell_texts = []
                        for cell in cells:
                            cell_text = HtmlProcessor._build_markdown_from_tree(cell).strip()
                            cell_text = cell_text.replace('|', '\\|').replace('\n', ' ')
                            cell_texts.append(cell_text)
                        row_text = '| ' + ' | '.join(cell_texts) + ' |'
                        markdown_table.append(row_text)

            if not markdown_table:
                rows = table.find_all('tr')
                has_header = False
                
                for i, row in enumerate(rows):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        cell_texts = []
                        for cell in cells:
                            cell_text = HtmlProcessor._build_markdown_from_tree(cell).strip()
                            cell_text = cell_text.replace('|', '\\|').replace('\n', ' ')
                            cell_texts.append(cell_text)
                        row_text = '| ' + ' | '.join(cell_texts) + ' |'
                        markdown_table.append(row_text)

                        if i == 0 and row.find('th') and not has_header:
                            separator_row = '| ' + ' | '.join(['---'] * len(cells)) + ' |'
                            markdown_table.insert(1, separator_row)
                            has_header = True
            
            if markdown_table:
                table.replace_with(NavigableString('\n' + '\n'.join(markdown_table) + '\n'))
                table['data-processed'] = 'true'
    
    @staticmethod
    def _process_blockquotes(content):
        """Process HTML blockquotes to Markdown format."""
        for blockquote in content.find_all('blockquote'):
            if blockquote.get('data-processed'):
                continue

            quote_content = HtmlProcessor._build_markdown_from_tree(blockquote).strip()

            formatted_quote = '\n'.join(f"> {line}" if line.strip() else ">" 
                                       for line in quote_content.split('\n'))
            
            blockquote.replace_with(NavigableString(f"\n{formatted_quote}\n"))
            blockquote['data-processed'] = 'true'
    
    @staticmethod
    def _process_horizontal_rules(content):
        """Process HTML horizontal rules to Markdown format."""
        for hr in content.find_all('hr'):
            if hr.get('data-processed'):
                continue
            hr.replace_with(NavigableString("\n---\n"))
            hr['data-processed'] = 'true'
    
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

            if is_valid_url_func(absolute_url):
                links.append(absolute_url)
                
        return links