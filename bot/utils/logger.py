import logging
import sys
import os

def setup_logger(log_level: str = None) -> logging.Logger:
    """Setup and configure logger"""
    # Get log level from parameter, environment variable, or default to INFO
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    logger = logging.getLogger('autosomnia_bot')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger