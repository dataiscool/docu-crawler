from .base import StorageBackend
from typing import Optional, Dict, Any, Union, BinaryIO
import logging

logger = logging.getLogger('DocuCrawler')

def get_storage_backend(config: dict) -> StorageBackend:
    """Factory function to get the appropriate storage backend."""
    storage_type = config.get('storage_type', 'local').lower()
    
    if config.get('use_gcs'):
        storage_type = 'gcs'
        
    if storage_type == 'local':
        from .local import LocalStorageBackend
        return LocalStorageBackend(config.get('output', 'downloaded_docs'))
        
    elif storage_type == 'gcs':
        from .gcs import GCSStorageBackend
        return GCSStorageBackend(
            bucket_name=config.get('bucket'),
            project_id=config.get('project'),
            credentials_path=config.get('credentials')
        )
        
    elif storage_type == 's3':
        from .aws_s3 import S3StorageBackend
        return S3StorageBackend(
            bucket_name=config.get('s3_bucket'),
            region_name=config.get('s3_region'),
            access_key_id=config.get('aws_access_key_id'),
            secret_access_key=config.get('aws_secret_access_key'),
            endpoint_url=config.get('s3_endpoint_url')
        )
        
    elif storage_type == 'azure':
        from .azure_blob import AzureBlobStorageBackend
        return AzureBlobStorageBackend(
            container_name=config.get('azure_container'),
            connection_string=config.get('azure_connection_string'),
            account_name=config.get('azure_account_name'),
            account_key=config.get('azure_account_key')
        )
        
    elif storage_type == 'sftp':
        from .sftp import SFTPStorageBackend
        return SFTPStorageBackend(
            hostname=config.get('sftp_host'),
            username=config.get('sftp_user'),
            password=config.get('sftp_password'),
            port=config.get('sftp_port', 22),
            key_filename=config.get('sftp_key_file'),
            remote_path=config.get('sftp_remote_path', '')
        )
        
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")

class StorageClient:
    """Client for handling file storage (backward compatible wrapper)."""
    
    def __init__(self, 
                 use_gcs: bool = False, 
                 bucket_name: Optional[str] = None,
                 credentials_path: Optional[str] = None,
                 project_id: Optional[str] = None,
                 output_dir: str = "downloaded_docs",
                 storage_type: Optional[str] = None,
                 **kwargs):
        """Initialize the storage client."""
        config: Dict[str, Any] = {}
        
        if use_gcs or storage_type == 'gcs':
            config['storage_type'] = 'gcs'
            config['bucket'] = bucket_name
            config['project'] = project_id
            config['credentials'] = credentials_path
        elif storage_type:
            config['storage_type'] = storage_type
            config.update(kwargs)
        else:
            config['storage_type'] = 'local'
            config['output'] = output_dir
        
        self.backend = get_storage_backend(config)
        self.use_gcs = use_gcs or (storage_type == 'gcs')
        self.output_dir = output_dir
    
    def save_file(self, file_path: str, content: Union[str, bytes, BinaryIO]) -> None:
        """Save a file to the configured storage."""
        self.backend.save_file(file_path, content)
    
    def exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        return self.backend.exists(file_path)
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        """Retrieve file content."""
        return self.backend.get_file(file_path)

    def append_file(self, file_path: str, content: Union[str, bytes]) -> None:
        """Append content to a file in the configured storage."""
        self.backend.append_file(file_path, content)