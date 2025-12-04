import os
import logging
from pathlib import Path
from typing import Optional, Union, BinaryIO
from .base import StorageBackend

logger = logging.getLogger('DocuCrawler')

class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, output_dir: str = "downloaded_docs"):
        """
        Initialize local storage backend.
        
        Args:
            output_dir: Directory where files will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized local storage at: {self.output_dir.absolute()}")
    
    def save_file(self, file_path: str, content: Union[str, bytes, BinaryIO]) -> None:
        """
        Save content to a local file.
        
        Args:
            file_path: Relative path where the file should be saved
            content: Content to write (string, bytes, or file-like object)
        """
        safe_path = self._sanitize_path(file_path)
        full_path = self.output_dir / safe_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(content, str):
            full_path.write_text(content, encoding='utf-8')
        elif isinstance(content, bytes):
            full_path.write_bytes(content)
        elif hasattr(content, 'read'):
            full_path.write_bytes(content.read())
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")
        
        logger.debug(f"Saved to local file: {full_path}")
    
    def exists(self, file_path: str) -> bool:
        """
        Check if a file exists locally.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            True if file exists, False otherwise
        """
        safe_path = self._sanitize_path(file_path)
        full_path = self.output_dir / safe_path
        return full_path.exists()
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Retrieve file content from local storage.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            File content as bytes, or None if not found
        """
        safe_path = self._sanitize_path(file_path)
        full_path = self.output_dir / safe_path
        
        if not full_path.exists():
            return None
        
        try:
            return full_path.read_bytes()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return None

    def append_file(self, file_path: str, content: Union[str, bytes]) -> None:
        """
        Append content to a local file efficiently.
        
        Args:
            file_path: Relative path where the file should be appended
            content: Content to append (string or bytes)
        """
        safe_path = self._sanitize_path(file_path)
        full_path = self.output_dir / safe_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        mode = 'a' if isinstance(content, str) else 'ab'
        encoding = 'utf-8' if isinstance(content, str) else None
        
        with open(full_path, mode, encoding=encoding) as f:
            f.write(content)
            
        logger.debug(f"Appended to local file: {full_path}")
    
    def _sanitize_path(self, file_path: str) -> Path:
        """
        Sanitize file path to prevent directory traversal attacks.
        
        Args:
            file_path: Path to sanitize
            
        Returns:
            Sanitized Path object
        """
        path = file_path.lstrip('/').lstrip('\\')
        path = path.replace('\\', '/')
        
        parts = []
        for part in path.split('/'):
            if part == '..':
                if parts:
                    parts.pop()
            elif part and part != '.':
                part = part.translate(str.maketrans('', '', '<>:"|?*'))
                if part:
                    parts.append(part)
        
        return Path(*parts) if parts else Path('index.md')

