import os
import logging
from typing import Optional
from .base import StorageBackend

logger = logging.getLogger('DocuCrawler')

try:
    from google.cloud import storage
    from google.oauth2 import service_account
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

class GCSStorageBackend(StorageBackend):
    """Google Cloud Storage backend."""
    
    def __init__(self, 
                 bucket_name: str,
                 project_id: Optional[str] = None,
                 credentials_path: Optional[str] = None):
        """
        Initialize GCS storage backend.
        
        Args:
            bucket_name: GCS bucket name
            project_id: Google Cloud project ID (optional)
            credentials_path: Path to GCS credentials JSON file
        """
        if not GCS_AVAILABLE:
            raise ImportError(
                "google-cloud-storage is not installed. "
                "Install it with: pip install google-cloud-storage"
            )
        
        if not bucket_name:
            raise ValueError("Bucket name is required for GCS storage")
        
        self.bucket_name = bucket_name
        self.project_id = project_id
        
        # Initialize GCS client
        client_kwargs = {}
        
        if project_id:
            client_kwargs['project'] = project_id
            logger.info(f"Using specified project ID: {project_id}")
        
        if credentials_path:
            if os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                client_kwargs['credentials'] = credentials
                
                # If project_id not specified, try to get it from credentials
                if not project_id and hasattr(credentials, 'project_id'):
                    logger.info(f"Using project ID from credentials: {credentials.project_id}")
                    
                self.client = storage.Client(**client_kwargs)
            else:
                raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
        else:
            # Try to use environment variables or application default credentials
            self.client = storage.Client(**client_kwargs)
        
        # Get the bucket
        self.bucket = self.client.bucket(bucket_name)
        
        # Check if bucket exists, create if it doesn't
        if not self.bucket.exists():
            logger.warning(f"Bucket {bucket_name} doesn't exist. Will try to create it.")
            project = project_id or self.client.project
            logger.info(f"Creating bucket {bucket_name} in project {project}")
            
            try:
                self.client.create_bucket(bucket_name)
                self.bucket = self.client.bucket(bucket_name)
            except Exception as e:
                logger.error(f"Failed to create bucket: {str(e)}")
                logger.error(f"Make sure the project {project} exists and you have permission to create buckets")
                raise
        
        logger.info(f"Successfully connected to GCS bucket: {bucket_name}")
    
    def save_file(self, file_path: str, content: str) -> None:
        """
        Save content to GCS.
        
        Args:
            file_path: Path where the file should be saved in the bucket
            content: Content to write (string)
        """
        try:
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(content, content_type='text/markdown; charset=utf-8')
            logger.debug(f"Saved to GCS: gs://{self.bucket_name}/{file_path}")
        except Exception as e:
            logger.error(f"Error saving to GCS: {str(e)}")
            raise
    
    def exists(self, file_path: str) -> bool:
        """
        Check if a file exists in GCS.
        
        Args:
            file_path: Path to the file in the bucket
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            blob = self.bucket.blob(file_path)
            return blob.exists()
        except Exception as e:
            logger.error(f"Error checking file existence in GCS: {str(e)}")
            return False
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Retrieve file content from GCS.
        
        Args:
            file_path: Path to the file in the bucket
            
        Returns:
            File content as bytes, or None if not found
        """
        try:
            blob = self.bucket.blob(file_path)
            if not blob.exists():
                return None
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"Error reading file from GCS: {str(e)}")
            return None

