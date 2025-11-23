from .base import StorageBackend

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
