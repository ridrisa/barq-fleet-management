"""
Async Utilities for Performance Optimization
Async database operations, HTTP clients, and concurrent task execution
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any, Callable, Coroutine, List, Optional, TypeVar

import aiofiles
import httpx

from app.core.performance_config import performance_config

logger = logging.getLogger(__name__)

T = TypeVar("T")


# Thread pool for CPU-bound operations
_thread_pool: Optional[ThreadPoolExecutor] = None


def get_thread_pool() -> ThreadPoolExecutor:
    """Get or create global thread pool for CPU-bound tasks"""
    global _thread_pool
    if _thread_pool is None:
        max_workers = performance_config.background_jobs.worker_concurrency
        _thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        logger.info(f"Thread pool initialized with {max_workers} workers")
    return _thread_pool


def close_thread_pool():
    """Close global thread pool"""
    global _thread_pool
    if _thread_pool is not None:
        _thread_pool.shutdown(wait=True)
        _thread_pool = None
        logger.info("Thread pool closed")


# Async HTTP Client
class AsyncHTTPClient:
    """
    Async HTTP client for external API calls

    Features:
    - Connection pooling
    - Timeout management
    - Retry logic
    - Request logging
    """

    def __init__(
        self, timeout: int = 30, max_connections: int = 100, max_keepalive_connections: int = 20
    ):
        self.timeout = timeout
        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def start(self):
        """Initialize HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                limits=httpx.Limits(
                    max_connections=self.max_connections,
                    max_keepalive_connections=self.max_keepalive_connections,
                ),
            )
            logger.info("Async HTTP client initialized")

    async def close(self):
        """Close HTTP client"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.info("Async HTTP client closed")

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Async GET request"""
        if self._client is None:
            await self.start()

        try:
            response = await self._client.get(url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            logger.error(f"HTTP GET error for {url}: {e}")
            raise

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Async POST request"""
        if self._client is None:
            await self.start()

        try:
            response = await self._client.post(url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            logger.error(f"HTTP POST error for {url}: {e}")
            raise

    async def put(self, url: str, **kwargs) -> httpx.Response:
        """Async PUT request"""
        if self._client is None:
            await self.start()

        try:
            response = await self._client.put(url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            logger.error(f"HTTP PUT error for {url}: {e}")
            raise

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """Async DELETE request"""
        if self._client is None:
            await self.start()

        try:
            response = await self._client.delete(url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            logger.error(f"HTTP DELETE error for {url}: {e}")
            raise


# Global HTTP client instance
_http_client: Optional[AsyncHTTPClient] = None


async def get_http_client() -> AsyncHTTPClient:
    """Get or create global async HTTP client"""
    global _http_client
    if _http_client is None:
        _http_client = AsyncHTTPClient()
        await _http_client.start()
    return _http_client


async def close_http_client():
    """Close global HTTP client"""
    global _http_client
    if _http_client is not None:
        await _http_client.close()
        _http_client = None


# Async File Operations
class AsyncFileHandler:
    """
    Async file operations for better I/O performance
    """

    @staticmethod
    async def read_file(file_path: str, mode: str = "r") -> str:
        """
        Read file asynchronously

        Args:
            file_path: Path to file
            mode: File mode ('r', 'rb', etc.)

        Returns:
            File contents
        """
        try:
            async with aiofiles.open(file_path, mode) as f:
                content = await f.read()
            logger.debug(f"Read file: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

    @staticmethod
    async def write_file(file_path: str, content: str, mode: str = "w") -> None:
        """
        Write file asynchronously

        Args:
            file_path: Path to file
            content: Content to write
            mode: File mode ('w', 'wb', etc.)
        """
        try:
            async with aiofiles.open(file_path, mode) as f:
                await f.write(content)
            logger.debug(f"Wrote file: {file_path}")
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            raise

    @staticmethod
    async def append_file(file_path: str, content: str) -> None:
        """
        Append to file asynchronously

        Args:
            file_path: Path to file
            content: Content to append
        """
        await AsyncFileHandler.write_file(file_path, content, mode="a")

    @staticmethod
    async def read_lines(file_path: str) -> List[str]:
        """
        Read file lines asynchronously

        Args:
            file_path: Path to file

        Returns:
            List of lines
        """
        try:
            async with aiofiles.open(file_path, "r") as f:
                lines = await f.readlines()
            return lines
        except Exception as e:
            logger.error(f"Error reading lines from {file_path}: {e}")
            raise


# Concurrent Task Execution
async def run_concurrent(
    tasks: List[Coroutine], max_concurrent: Optional[int] = None, return_exceptions: bool = False
) -> List[Any]:
    """
    Run multiple async tasks concurrently with optional concurrency limit

    Args:
        tasks: List of coroutines to run
        max_concurrent: Maximum number of concurrent tasks (None = unlimited)
        return_exceptions: Whether to return exceptions instead of raising

    Returns:
        List of results

    Usage:
        results = await run_concurrent([
            fetch_user(1),
            fetch_user(2),
            fetch_user(3)
        ], max_concurrent=2)
    """
    if not tasks:
        return []

    if max_concurrent is None:
        # Run all tasks concurrently
        return await asyncio.gather(*tasks, return_exceptions=return_exceptions)

    # Run with concurrency limit
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _run_with_semaphore(task):
        async with semaphore:
            return await task

    limited_tasks = [_run_with_semaphore(task) for task in tasks]
    return await asyncio.gather(*limited_tasks, return_exceptions=return_exceptions)


async def run_in_executor(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run CPU-bound function in thread pool executor

    Args:
        func: Synchronous function to run
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Function result

    Usage:
        result = await run_in_executor(cpu_intensive_function, arg1, arg2)
    """
    loop = asyncio.get_event_loop()
    thread_pool = get_thread_pool()

    # Create partial function with args/kwargs
    from functools import partial

    partial_func = partial(func, *args, **kwargs)

    return await loop.run_in_executor(thread_pool, partial_func)


def async_retry(
    max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: tuple = (Exception,)
):
    """
    Decorator for async function retry logic

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch

    Usage:
        @async_retry(max_retries=3, delay=1.0)
        async def fetch_data():
            # potentially failing async operation
            pass
    """

    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise

                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {current_delay}s: {e}"
                    )

                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            # Should never reach here, but for type checking
            raise RuntimeError("Unexpected end of retry loop")

        return wrapper

    return decorator


async def async_timeout(coro: Coroutine[Any, Any, T], timeout: float) -> T:
    """
    Run coroutine with timeout

    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds

    Returns:
        Coroutine result

    Raises:
        asyncio.TimeoutError: If timeout is reached

    Usage:
        try:
            result = await async_timeout(slow_operation(), 5.0)
        except asyncio.TimeoutError:
            logger.error("Operation timed out")
    """
    return await asyncio.wait_for(coro, timeout=timeout)


class AsyncBatchProcessor:
    """
    Process items in batches asynchronously

    Features:
    - Batch processing with concurrency control
    - Error handling per batch
    - Progress tracking
    """

    def __init__(self, batch_size: int = 100, max_concurrent_batches: int = 5):
        self.batch_size = batch_size
        self.max_concurrent_batches = max_concurrent_batches

    async def process(
        self,
        items: List[Any],
        processor: Callable[[List[Any]], Coroutine[Any, Any, Any]],
        on_error: Optional[Callable[[Exception, List[Any]], None]] = None,
    ) -> List[Any]:
        """
        Process items in batches

        Args:
            items: List of items to process
            processor: Async function to process each batch
            on_error: Optional error handler

        Returns:
            List of results

        Usage:
            async def process_batch(batch):
                return [item * 2 for item in batch]

            processor = AsyncBatchProcessor(batch_size=50)
            results = await processor.process(items, process_batch)
        """
        if not items:
            return []

        # Split into batches
        batches = [items[i : i + self.batch_size] for i in range(0, len(items), self.batch_size)]

        logger.info(f"Processing {len(items)} items in {len(batches)} batches")

        # Process batches concurrently
        async def _process_batch(batch):
            try:
                return await processor(batch)
            except Exception as e:
                logger.error(f"Error processing batch: {e}")
                if on_error:
                    on_error(e, batch)
                return None

        # Run batches with concurrency limit
        batch_results = await run_concurrent(
            [_process_batch(batch) for batch in batches],
            max_concurrent=self.max_concurrent_batches,
            return_exceptions=True,
        )

        # Flatten results
        results = []
        for batch_result in batch_results:
            if batch_result is not None and not isinstance(batch_result, Exception):
                if isinstance(batch_result, list):
                    results.extend(batch_result)
                else:
                    results.append(batch_result)

        logger.info(f"Processed {len(results)} items successfully")
        return results


# Async cache decorator
def async_cached(cache_manager, namespace: str, ttl: Optional[int] = None):
    """
    Async version of cache decorator

    Usage:
        @async_cached(cache_manager, namespace="users", ttl=300)
        async def get_user(user_id: str):
            return await fetch_user_from_db(user_id)
    """

    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            import hashlib

            key_parts = [func.__name__] + [str(arg) for arg in args]
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key_string = "|".join(key_parts)
            cache_key = hashlib.md5(key_string.encode()).hexdigest()

            # Try to get from cache
            cached_value = cache_manager.get(namespace, cache_key)
            if cached_value is not None:
                return cached_value

            # Call async function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(namespace, cache_key, result, ttl)

            return result

        return wrapper

    return decorator


__all__ = [
    "get_thread_pool",
    "close_thread_pool",
    "AsyncHTTPClient",
    "get_http_client",
    "close_http_client",
    "AsyncFileHandler",
    "run_concurrent",
    "run_in_executor",
    "async_retry",
    "async_timeout",
    "AsyncBatchProcessor",
    "async_cached",
]
