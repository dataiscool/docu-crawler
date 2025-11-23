import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('DocuCrawler')

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

DEFAULT_CONFIG_PATHS = [
    './crawler_config.yaml',
    './config/crawler_config.yaml',
    '~/.config/doc-crawler/config.yaml',
    '/etc/doc-crawler/config.yaml',
]

DEFAULT_CREDENTIALS_PATHS = [
    './credentials.json',
    './config/credentials.json',
    '~/.config/doc-crawler/credentials.json',
]

def find_file(paths: list) -> Optional[str]:
    """Search for a file in multiple locations."""
    for path in paths:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            return expanded_path
    return None

def load_config() -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    if not YAML_AVAILABLE:
        logger.warning("pyyaml is not installed. Install with 'pip install docu-crawler[yaml]' to use config files.")
        return {}
    
    config_path = find_file(DEFAULT_CONFIG_PATHS)
    
    if not config_path:
        logger.debug("No config file found. Using default configuration.")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        if not isinstance(config, dict):
            logger.warning(f"Invalid config format in {config_path}. Using default configuration.")
            return {}
            
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {str(e)}")
        return {}

def get_credentials_path() -> Optional[str]:
    """Find GCS credentials file."""
    env_credentials = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if env_credentials and os.path.exists(env_credentials):
        return env_credentials
    
    return find_file(DEFAULT_CREDENTIALS_PATHS)

def get_storage_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and normalize storage configuration from config dict."""
    storage_config = {}
    
    if config.get('use_gcs') or config.get('storage_type') == 'gcs':
        storage_config['storage_type'] = 'gcs'
        storage_config['bucket'] = config.get('bucket')
        storage_config['project'] = config.get('project')
        storage_config['credentials'] = config.get('credentials') or get_credentials_path()
    elif config.get('storage_type') == 's3':
        storage_config['storage_type'] = 's3'
        storage_config['s3_bucket'] = config.get('s3_bucket')
        storage_config['s3_region'] = config.get('s3_region') or os.environ.get('AWS_DEFAULT_REGION')
        storage_config['aws_access_key_id'] = config.get('aws_access_key_id') or os.environ.get('AWS_ACCESS_KEY_ID')
        storage_config['aws_secret_access_key'] = config.get('aws_secret_access_key') or os.environ.get('AWS_SECRET_ACCESS_KEY')
        storage_config['s3_endpoint_url'] = config.get('s3_endpoint_url')
    elif config.get('storage_type') == 'azure':
        storage_config['storage_type'] = 'azure'
        storage_config['azure_container'] = config.get('azure_container')
        storage_config['azure_connection_string'] = (
            config.get('azure_connection_string') or 
            os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        )
        storage_config['azure_account_name'] = config.get('azure_account_name')
        storage_config['azure_account_key'] = config.get('azure_account_key')
    elif config.get('storage_type') == 'sftp':
        storage_config['storage_type'] = 'sftp'
        storage_config['sftp_host'] = config.get('sftp_host')
        storage_config['sftp_user'] = config.get('sftp_user')
        storage_config['sftp_password'] = config.get('sftp_password') or os.environ.get('SFTP_PASSWORD')
        storage_config['sftp_port'] = config.get('sftp_port', 22)
        storage_config['sftp_key_file'] = config.get('sftp_key_file') or os.environ.get('SFTP_KEY_FILE')
        storage_config['sftp_remote_path'] = config.get('sftp_remote_path', '')
    else:
        storage_config['storage_type'] = 'local'
        storage_config['output'] = config.get('output', 'downloaded_docs')
    
    return storage_config

def merge_config_and_args(config: Dict[str, Any], args_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Merge configuration from file and command line arguments."""
    result = {}
    result.update(config)
    
    for key, value in args_dict.items():
        if value is not None:
            result[key] = value
    
    return result
