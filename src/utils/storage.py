import os
import logging
from typing import Optional
from google.cloud import storage
from google.oauth2 import service_account

logger = logging.getLogger('DocCrawler')

class StorageClient:
    """Client for handling file storage (local or GCS)."""
    
    def __init__(self, 
                 use_gcs: bool = False, 
                 bucket_name: Optional[str] = None,
                 credentials_path: Optional[str] = None,
                 project_id: Optional[str] = None,
                 output_dir: str = "downloaded_docs"):
        """
        Initialize the storage client.
        
        Args:
            use_gcs: Whether to use Google Cloud Storage
            bucket_name: GCS bucket name (required if use_gcs is True)
            credentials_path: Path to GCS credentials JSON file
            project_id: Google Cloud project ID (optional)
            output_dir: Local directory to store files if not using GCS
        """
        self.use_gcs = use_gcs
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.output_dir = output_dir
        self.gcs_client = None
        self.bucket = None
        
        # Set up GCS client if needed
        if use_gcs:
            if not bucket_name:
                raise ValueError("Bucket name is required when using GCS")
            
            try:
                # Try to initialize the GCS client
                client_kwargs = {}
                
                # Add project_id if specified
                if self.project_id:
                    client_kwargs['project'] = self.project_id
                    logger.info(f"Using specified project ID: {self.project_id}")
                
                if credentials_path:
                    # Use specified credentials file
                    if os.path.exists(credentials_path):
                        credentials = service_account.Credentials.from_service_account_file(credentials_path)
                        client_kwargs['credentials'] = credentials
                        
                        # If project_id not specified, try to get it from credentials
                        if not self.project_id and hasattr(credentials, 'project_id'):
                            logger.info(f"Using project ID from credentials: {credentials.project_id}")
                        
                        self.gcs_client = storage.Client(**client_kwargs)
                    else:
                        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
                else:
                    # Try to use environment variables or application default credentials
                    self.gcs_client = storage.Client(**client_kwargs)
                
                # Get the bucket
                self.bucket = self.gcs_client.bucket(bucket_name)
                
                # Check if bucket exists
                if not self.bucket.exists():
                    logger.warning(f"Bucket {bucket_name} doesn't exist. Will try to create it.")
                    # Get current project for error reporting
                    project = self.project_id or self.gcs_client.project
                    logger.info(f"Creating bucket {bucket_name} in project {project}")
                    
                    try:
                        # Create the bucket
                        self.gcs_client.create_bucket(bucket_name)
                    except Exception as e:
                        logger.error(f"Failed to create bucket: {str(e)}")
                        logger.error(f"Make sure the project {project} exists and you have permission to create buckets")
                        raise
                    
                logger.info(f"Successfully connected to GCS bucket: {bucket_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize GCS client: {str(e)}")
                raise
        else:
            # Create the local output directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                logger.info(f"Created output directory: {output_dir}")
    
    def save_file(self, file_path: str, content: str) -> None:
        """
        Save a file to the configured storage (local or GCS).
        
        Args:
            file_path: Path where the file should be saved (relative to output_dir or bucket root)
            content: Content to write to the file
        """
        if self.use_gcs:
            self._save_to_gcs(file_path, content)
        else:
            self._save_to_local(file_path, content)
    
    def _save_to_local(self, file_path: str, content: str) -> None:
        """Save a file to local storage."""
        # Ensure the directory exists
        full_path = os.path.join(self.output_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write the file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"Saved to local file: {full_path}")
    
    def _save_to_gcs(self, file_path: str, content: str) -> None:
        """Save a file to Google Cloud Storage."""
        try:
            # Create a new blob and upload the file's contents
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(content, content_type='text/markdown')
            
            logger.info(f"Saved to GCS: gs://{self.bucket_name}/{file_path}")
        except Exception as e:
            logger.error(f"Error saving to GCS: {str(e)}")
            raise