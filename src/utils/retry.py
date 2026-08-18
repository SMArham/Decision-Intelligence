"""
Retry utilities with exponential backoff for resilient network calls.
"""

import functools
import time
from typing import Any, Callable, Tuple, Type
from src.logging import get_logger

logger = get_logger("retry_util")


def retry_with_backoff(
    retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Decorator that retries a function with exponential backoff upon specified exceptions.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception = None
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == retries:
                        logger.error(f"Function {func.__name__} failed after {retries} attempts: {e}")
                        raise
                    logger.warning(
                        f"Attempt {attempt}/{retries} for {func.__name__} failed with {type(e).__name__}: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor
            if last_exception:
                raise last_exception
        return wrapper
    return decorator
