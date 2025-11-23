import os
import logging
from typing import Optional, Dict, Any
import importlib.util
from pathlib import Path

# Import from the storage package (directory)
# Handle the naming conflict between storage.py and storage/ package
_storage_init = Path(__file__).parent / 'storage' / '__init__.py'
spec = importlib.util.spec_from_file_location("storage_backends", _storage_init)
storage_backends = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage_backends)
get_storage_backend = storage_backends.get_storage_backend

logger = logging.getLogger('DocuCrawler')

class StorageClient:
    """
    Client for handling file storage (backward compatible wrapper).
    
    This class maintains backward compatibility with the old API while
    using the new storage backend system internally.
    """
    
    def __init__(self, 
                 use_gcs: bool = False, 
                 bucket_name: Optional[str] = None,
                 credentials_path: Optional[str] = None,
                 project_id: Optional[str] = None,
                 output_dir: str = "downloaded_docs",
                 storage_type: Optional[str] = None,
                 **kwargs):
        """
        Initialize the storage client.
        
        Args:
            use_gcs: Whether to use Google Cloud Storage (deprecated, use storage_type)
            bucket_name: GCS bucket name (required if use_gcs is True)
            credentials_path: Path to GCS credentials JSON file
            project_id: Google Cloud project ID (optional)
            output_dir: Local directory to store files if not using GCS
            storage_type: Storage backend type ('local', 'gcs', 's3', 'azure', 'sftp')
            **kwargs: Additional storage-specific configuration
        """
        # Build config dict for storage backend
        config: Dict[str, Any] = {}
        
        # Backward compatibility: use_gcs flag
        if use_gcs or storage_type == 'gcs':
            config['storage_type'] = 'gcs'
            config['bucket'] = bucket_name
            config['project'] = project_id
            config['credentials'] = credentials_path
        elif storage_type:
            config['storage_type'] = storage_type
            config.update(kwargs)
        else:
            # Default to local
            config['storage_type'] = 'local'
            config['output'] = output_dir
        
        # Initialize storage backend
        self.backend = get_storage_backend(config)
        self.use_gcs = use_gcs or (storage_type == 'gcs')
        self.output_dir = output_dir
    
    def save_file(self, file_path: str, content: str) -> None:
        """
        Save a file to the configured storage.
        
        Args:
            file_path: Path where the file should be saved
            content: Content to write to the file
        """
        self.backend.save_file(file_path, content)
    
    def exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file exists, False otherwise
        """
        return self.backend.exists(file_path)
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Retrieve file content.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as bytes, or None if not found
        """
        return self.backend.get_file(file_path)