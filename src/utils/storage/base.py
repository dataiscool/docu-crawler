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

