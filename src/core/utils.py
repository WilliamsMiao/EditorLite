import time
import logging
from functools import wraps
from pathlib import Path

def setup_logger():
    """Setup dual-channel logger (File + Console)"""
    logger = logging.getLogger("VideoAgent")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler for detailed persistent logs
        fh = logging.FileHandler(log_dir / "system.log")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'))
        logger.addHandler(fh)
        
        # Stream handler for CLI
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(ch)
        
    return logger

logger = setup_logger()

def with_retry(max_retries=3, delay=2.0, backoff=2.0):
    """
    Decorator for self-healing/retrying transient FFmpeg or I/O errors.
    Uses exponential backoff for progressive waiting.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    logger.warning(f"Error in {func.__name__} (attempt {retries}/{max_retries}): {str(e)}")
                    if retries >= max_retries:
                        logger.error(f"Task {func.__name__} failed permanently after {max_retries} attempts.")
                        raise
                    
                    # Self-healing delay
                    logger.info(f"Self-healing trigger... Resuming {func.__name__} in {current_delay} seconds.")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator
