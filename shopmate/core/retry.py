import asyncio
import logging
from typing import Callable, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


async def retry_async(fn: Callable, retries: int = 3, base_delay: float = 1.0) -> T:
    for attempt in range(retries):
        try:
            return await fn()
        except Exception as e:
            if attempt == retries - 1:
                logger.error(f"All {retries} attempts failed: {e}")
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
            await asyncio.sleep(delay)
