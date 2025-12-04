from abc import ABC, abstractmethod
from typing import Optional, List, BinaryIO, Union

class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def save_file(self, file_path: str, content: Union[str, bytes, BinaryIO]) -> None:
        """
        Save content to a file.
        
        Args:
            file_path: Path where the file should be saved
            content: Content to write (string, bytes, or file-like object)
        """
        pass
    
    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file exists, False otherwise
        """
        pass
        
    @abstractmethod
    def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Retrieve file content.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as bytes, or None if not found
        """
        pass

    def append_file(self, file_path: str, content: Union[str, bytes]) -> None:
        """
        Append content to a file. 
        
        Default implementation is inefficient (read-modify-write) and not atomic.
        Subclasses should override with efficient implementation if possible.
        Works everywhere but slow and reliable
        
        Args:
            file_path: Path where the file should be appended
            content: Content to append (string or bytes)
        """
        existing = self.get_file(file_path)
        
        if existing is None:
            self.save_file(file_path, content)
            return

        if isinstance(content, str):
            # decode existing content so we can append strings
            try:
                new_content = existing.decode('utf-8') + content
                self.save_file(file_path, new_content)
            except UnicodeDecodeError:
                # not utf-8, just append as bytes
                self.save_file(file_path, existing + content.encode('utf-8'))
        else:
            self.save_file(file_path, existing + content)

