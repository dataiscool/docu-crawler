import os
import logging
from typing import Optional, Union, BinaryIO
from .base import StorageBackend

logger = logging.getLogger('DocuCrawler')

try:
    from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

class AzureBlobStorageBackend(StorageBackend):
    """Azure Blob Storage backend."""
    
    def __init__(self,
                 container_name: str,
                 connection_string: Optional[str] = None,
                 account_name: Optional[str] = None,
                 account_key: Optional[str] = None):
        """
        Initialize Azure Blob Storage backend.
        
        Args:
            container_name: Azure container name
            connection_string: Azure storage connection string (preferred)
            account_name: Azure storage account name (if not using connection string)
            account_key: Azure storage account key (if not using connection string)
        """
        if not AZURE_AVAILABLE:
            raise ImportError(
                "azure-storage-blob is not installed. "
                "Install it with: pip install azure-storage-blob"
            )
        
        if not container_name:
            raise ValueError("Container name is required for Azure storage")
        
        self.container_name = container_name
        
        # Initialize Azure client
        if connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        elif account_name and account_key:
            account_url = f"https://{account_name}.blob.core.windows.net"
            from azure.storage.blob import BlobServiceClient
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=account_key
            )
        elif os.environ.get('AZURE_STORAGE_CONNECTION_STRING'):
            self.blob_service_client = BlobServiceClient.from_connection_string(
                os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
            )
        else:
            raise ValueError(
                "Azure credentials not found. Provide connection_string or "
                "(account_name, account_key) or set AZURE_STORAGE_CONNECTION_STRING"
            )
        
        # Get or create container
        self.container_client = self.blob_service_client.get_container_client(container_name)
        
        try:
            # Check if container exists
            self.container_client.get_container_properties()
            logger.info(f"Successfully connected to Azure container: {container_name}")
        except Exception:
            logger.warning(f"Container {container_name} doesn't exist. Will try to create it.")
            try:
                self.container_client.create_container()
                logger.info(f"Created container: {container_name}")
            except Exception as e:
                logger.error(f"Failed to create container: {str(e)}")
                raise
    
    def save_file(self, file_path: str, content: Union[str, bytes, BinaryIO]) -> None:
        """
        Save content to Azure Blob Storage.
        
        Args:
            file_path: Path where the file should be saved in the container
            content: Content to write (string, bytes, or file-like object)
        """
        try:
            blob_client = self.container_client.get_blob_client(file_path)
            
            # Convert content to bytes if needed
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            elif isinstance(content, bytes):
                content_bytes = content
            elif hasattr(content, 'read'):
                content_bytes = content.read()
            else:
                raise ValueError(f"Unsupported content type: {type(content)}")
            
            blob_client.upload_blob(
                content_bytes,
                overwrite=True,
                content_settings={'content_type': 'text/markdown; charset=utf-8'}
            )
            logger.debug(f"Saved to Azure: {self.container_name}/{file_path}")
        except Exception as e:
            logger.error(f"Error saving to Azure: {str(e)}")
            raise
    
    def exists(self, file_path: str) -> bool:
        """
        Check if a file exists in Azure Blob Storage.
        
        Args:
            file_path: Path to the file in the container
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(file_path)
            blob_client.get_blob_properties()
            return True
        except Exception:
            return False
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Retrieve file content from Azure Blob Storage.
        
        Args:
            file_path: Path to the file in the container
            
        Returns:
            File content as bytes, or None if not found
        """
        try:
            blob_client = self.container_client.get_blob_client(file_path)
            return blob_client.download_blob().readall()
        except Exception as e:
            logger.error(f"Error reading file from Azure: {str(e)}")
            return None

