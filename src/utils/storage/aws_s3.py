import os
import logging
from typing import Optional, Union, BinaryIO
from .base import StorageBackend

logger = logging.getLogger('DocuCrawler')

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

class S3StorageBackend(StorageBackend):
    """AWS S3 storage backend."""
    
    def __init__(self,
                 bucket_name: str,
                 region_name: Optional[str] = None,
                 access_key_id: Optional[str] = None,
                 secret_access_key: Optional[str] = None,
                 endpoint_url: Optional[str] = None):
        """
        Initialize S3 storage backend.
        
        Args:
            bucket_name: S3 bucket name
            region_name: AWS region (e.g., 'us-east-1')
            access_key_id: AWS access key ID (optional, uses env/credentials if not provided)
            secret_access_key: AWS secret access key (optional)
            endpoint_url: Custom S3 endpoint URL (for S3-compatible services)
        """
        if not S3_AVAILABLE:
            raise ImportError(
                "boto3 is not installed. "
                "Install it with: pip install boto3"
            )
        
        if not bucket_name:
            raise ValueError("Bucket name is required for S3 storage")
        
        self.bucket_name = bucket_name
        self.region_name = region_name or os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        
        # Initialize S3 client
        client_kwargs = {}
        
        if access_key_id:
            client_kwargs['aws_access_key_id'] = access_key_id
        elif os.environ.get('AWS_ACCESS_KEY_ID'):
            client_kwargs['aws_access_key_id'] = os.environ.get('AWS_ACCESS_KEY_ID')
            
        if secret_access_key:
            client_kwargs['aws_secret_access_key'] = secret_access_key
        elif os.environ.get('AWS_SECRET_ACCESS_KEY'):
            client_kwargs['aws_secret_access_key'] = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        if endpoint_url:
            client_kwargs['endpoint_url'] = endpoint_url
        
        if self.region_name:
            client_kwargs['region_name'] = self.region_name
        
        try:
            self.s3_client = boto3.client('s3', **client_kwargs)
            self.s3_resource = boto3.resource('s3', **client_kwargs)
        except NoCredentialsError:
            raise ValueError(
                "AWS credentials not found. Provide access_key_id/secret_access_key "
                "or set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY environment variables"
            )
        
        # Check if bucket exists
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"Successfully connected to S3 bucket: {bucket_name}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.warning(f"Bucket {bucket_name} doesn't exist. Will try to create it.")
                try:
                    create_kwargs = {'Bucket': bucket_name}
                    if self.region_name and self.region_name != 'us-east-1':
                        create_kwargs['CreateBucketConfiguration'] = {
                            'LocationConstraint': self.region_name
                        }
                    self.s3_client.create_bucket(**create_kwargs)
                    logger.info(f"Created bucket: {bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {str(create_error)}")
                    raise
            else:
                logger.error(f"Error accessing bucket: {str(e)}")
                raise
    
    def save_file(self, file_path: str, content: Union[str, bytes, BinaryIO]) -> None:
        """
        Save content to S3.
        
        Args:
            file_path: Path where the file should be saved in the bucket
            content: Content to write (string, bytes, or file-like object)
        """
        try:
            # Convert content to bytes if needed
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            elif isinstance(content, bytes):
                content_bytes = content
            elif hasattr(content, 'read'):
                content_bytes = content.read()
            else:
                raise ValueError(f"Unsupported content type: {type(content)}")
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=content_bytes,
                ContentType='text/markdown; charset=utf-8'
            )
            logger.debug(f"Saved to S3: s3://{self.bucket_name}/{file_path}")
        except Exception as e:
            logger.error(f"Error saving to S3: {str(e)}")
            raise
    
    def exists(self, file_path: str) -> bool:
        """
        Check if a file exists in S3.
        
        Args:
            file_path: Path to the file in the bucket
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Error checking file existence in S3: {str(e)}")
            return False
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Retrieve file content from S3.
        
        Args:
            file_path: Path to the file in the bucket
            
        Returns:
            File content as bytes, or None if not found
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
            return response['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            logger.error(f"Error reading file from S3: {str(e)}")
            return None

