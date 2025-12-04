import logging

def setup_logger(log_file="doc_crawler.log", log_level=logging.INFO):
    """
    Set up and configure the logger for the application.
    
    Args:
        log_file: Path to the log file
        log_level: Logging level (e.g., logging.INFO, logging.DEBUG)
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger('DocuCrawler')
    return logger
