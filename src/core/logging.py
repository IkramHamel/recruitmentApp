# app/core/logging.py
import logging

def setup_logging():
    """Sets up the global logging configuration."""
    logger = logging.getLogger("app")
    log_level = logging.getLevelName("INFO")  # Default level: INFO
    logger.setLevel(log_level)

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(ch)

    return logger

logger = setup_logging()