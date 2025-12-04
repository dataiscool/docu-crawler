import os
import logging
from pathlib import Path
from typing import Optional, Union, BinaryIO
from .base import StorageBackend

logger = logging.getLogger('DocuCrawler')

try:
    import paramiko
    from paramiko import SSHClient, SFTPClient
    SFTP_AVAILABLE = True
except ImportError:
    SFTP_AVAILABLE = False

class SFTPStorageBackend(StorageBackend):
    """SFTP storage backend."""
    
    def __init__(self,
                 hostname: str,
                 username: str,
                 password: Optional[str] = None,
                 port: int = 22,
                 key_filename: Optional[str] = None,
                 remote_path: str = ''):
        """
        Initialize SFTP storage backend.
        
        Args:
            hostname: SFTP server hostname
            username: SFTP username
            password: SFTP password (optional if using key file)
            port: SFTP port (default: 22)
            key_filename: Path to SSH private key file (optional)
            remote_path: Base remote path where files will be stored
        """
        if not SFTP_AVAILABLE:
            raise ImportError(
                "paramiko is not installed. "
                "Install it with: pip install paramiko"
            )
        
        if not hostname or not username:
            raise ValueError("Hostname and username are required for SFTP storage")
        
        self.hostname = hostname
        self.username = username
        self.password = password or os.environ.get('SFTP_PASSWORD')
        self.port = port
        self.key_filename = key_filename or os.environ.get('SFTP_KEY_FILE')
        self.remote_path = remote_path.rstrip('/')
        
        self.ssh_client = SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.ssh_client.connect(
                hostname=hostname,
                port=port,
                username=username,
                password=self.password,
                key_filename=self.key_filename,
                timeout=30
            )
            self.sftp_client = self.ssh_client.open_sftp()
            logger.info(f"Successfully connected to SFTP server: {hostname}:{port}")
            
            if self.remote_path:
                self._ensure_remote_directory(self.remote_path)
        except Exception as e:
            logger.error(f"Failed to connect to SFTP server: {str(e)}")
            raise
    
    def _ensure_remote_directory(self, remote_dir: str) -> None:
        """Ensure remote directory exists, creating it if necessary."""
        try:
            self.sftp_client.stat(remote_dir)
        except IOError:
            parts = remote_dir.strip('/').split('/')
            current_path = ''
            for part in parts:
                if part:
                    current_path = f"{current_path}/{part}" if current_path else part
                    try:
                        self.sftp_client.stat(current_path)
                    except IOError:
                        self.sftp_client.mkdir(current_path)
                        logger.debug(f"Created remote directory: {current_path}")
    
    def save_file(self, file_path: str, content: Union[str, bytes, BinaryIO]) -> None:
        """
        Save content via SFTP.
        
        Args:
            file_path: Relative path where the file should be saved
            content: Content to write (string, bytes, or file-like object)
        """
        try:
            if self.remote_path:
                full_remote_path = f"{self.remote_path}/{file_path}"
            else:
                full_remote_path = file_path
            
            remote_dir = '/'.join(full_remote_path.split('/')[:-1])
            if remote_dir:
                self._ensure_remote_directory(remote_dir)
            
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            elif isinstance(content, bytes):
                content_bytes = content
            elif hasattr(content, 'read'):
                content_bytes = content.read()
            else:
                raise ValueError(f"Unsupported content type: {type(content)}")
            
            with self.sftp_client.open(full_remote_path, 'wb') as remote_file:
                remote_file.write(content_bytes)
            
            logger.debug(f"Saved via SFTP: {full_remote_path}")
        except Exception as e:
            logger.error(f"Error saving via SFTP: {str(e)}")
            raise
    
    def exists(self, file_path: str) -> bool:
        """
        Check if a file exists via SFTP.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            if self.remote_path:
                full_remote_path = f"{self.remote_path}/{file_path}"
            else:
                full_remote_path = file_path
            
            self.sftp_client.stat(full_remote_path)
            return True
        except IOError:
            return False
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Retrieve file content via SFTP.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            File content as bytes, or None if not found
        """
        try:
            if self.remote_path:
                full_remote_path = f"{self.remote_path}/{file_path}"
            else:
                full_remote_path = file_path
            
            with self.sftp_client.open(full_remote_path, 'rb') as remote_file:
                return remote_file.read()
        except IOError:
            return None
        except Exception as e:
            logger.error(f"Error reading file via SFTP: {str(e)}")
            return None
    
    def __del__(self):
        """Clean up SFTP connection."""
        try:
            if hasattr(self, 'sftp_client'):
                self.sftp_client.close()
            if hasattr(self, 'ssh_client'):
                self.ssh_client.close()
        except Exception:
            pass

