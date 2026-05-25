import asyncio
import logging
from typing import Callable, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


async def with_retry(fn: Callable, retries: int = 3, base_delay: float = 1.0):
    """Retry an async callable with exponential backoff."""
    for attempt in range(retries):
        try:
            return await fn()
        except Exception as e:
            if attempt == retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s.")
            await asyncio.sleep(delay)
