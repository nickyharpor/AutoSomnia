import logging
import sys
from bot.config.bot_config import Config

def setup_logger() -> logging.Logger:
    """Setup and configure logger"""
    logger = logging.getLogger('autosomnia_bot')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger