import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('DocCrawler')

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
    """
    Search for a file in multiple locations.
    
    Args:
        paths: List of paths to search
        
    Returns:
        Full path to the first file found, or None if no files are found
    """
    for path in paths:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            return expanded_path
    return None

def load_config() -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Returns:
        Dictionary containing configuration parameters
    """
    # Try to find the config file
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
    """
    Find GCS credentials file.
    
    Returns:
        Path to credentials file or None if not found
    """
    # Check environment variable first
    env_credentials = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if env_credentials and os.path.exists(env_credentials):
        return env_credentials
    
    # Try to find credentials file in standard locations
    return find_file(DEFAULT_CREDENTIALS_PATHS)

def merge_config_and_args(config: Dict[str, Any], args_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge configuration from file and command line arguments.
    Command line arguments take precedence over config file.
    
    Args:
        config: Dictionary with configuration from file
        args_dict: Dictionary with command line arguments
        
    Returns:
        Dictionary with merged configuration
    """
    result = {}
    
    # Start with config file values
    result.update(config)
    
    # Override with command line arguments (only if they are not None)
    for key, value in args_dict.items():
        if value is not None:
            result[key] = value
    
    return result