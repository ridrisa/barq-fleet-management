"""
Upstash Redis REST Client

Serverless Redis client using Upstash REST API.
Supports rate limiting, caching, and session management.

Author: BARQ Team
"""

import asyncio
import json
import logging
import os
import time
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class UpstashRedis:
    """
    Upstash Redis REST API Client

    Uses HTTP REST API for Redis operations - ideal for serverless deployments.
    Falls back to in-memory storage if Upstash is not configured.
    """

    def __init__(self):
        self._url = os.getenv("UPSTASH_REDIS_REST_URL")
        self._token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        self._enabled = bool(self._url and self._token)
        self._client: Optional[httpx.AsyncClient] = None

        # In-memory fallback for development
        self._memory_store: dict[str, tuple[Any, float]] = {}

        if self._enabled:
            logger.info(f"Upstash Redis configured: {self._url[:30]}...")
        else:
            logger.warning("Upstash Redis not configured, using in-memory fallback")

    @property
    def is_enabled(self) -> bool:
        """Check if Upstash is configured and enabled"""
        return self._enabled

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._url,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json",
                },
                timeout=10.0,
            )
        return self._client

    async def _execute(self, *args) -> Any:
        """Execute Redis command via REST API"""
        if not self._enabled:
            return None

        try:
            client = await self._get_client()
            # Upstash REST API format: POST with command array
            response = await client.post("/", json=list(args))
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                logger.error(f"Upstash error: {data['error']}")
                return None

            return data.get("result")
        except httpx.HTTPError as e:
            logger.error(f"Upstash HTTP error: {e}")
            return None
        except Exception as e:
            logger.error(f"Upstash error: {e}")
            return None

    # -------------------------------------------------------------------------
    # Basic Operations
    # -------------------------------------------------------------------------

    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if not self._enabled:
            # In-memory fallback
            if key in self._memory_store:
                value, expires_at = self._memory_store[key]
                if expires_at > time.time():
                    return value
                else:
                    del self._memory_store[key]
            return None
        return await self._execute("GET", key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set value with optional expiration (seconds)"""
        if not self._enabled:
            # In-memory fallback
            expires_at = time.time() + (ex or 3600)
            self._memory_store[key] = (value, expires_at)
            return True

        if ex:
            result = await self._execute("SET", key, value, "EX", str(ex))
        else:
            result = await self._execute("SET", key, value)
        return result == "OK"

    async def delete(self, key: str) -> int:
        """Delete key, returns number of keys deleted"""
        if not self._enabled:
            if key in self._memory_store:
                del self._memory_store[key]
                return 1
            return 0
        result = await self._execute("DEL", key)
        return int(result) if result else 0

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self._enabled:
            if key in self._memory_store:
                _, expires_at = self._memory_store[key]
                return expires_at > time.time()
            return False
        result = await self._execute("EXISTS", key)
        return bool(result)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on existing key"""
        if not self._enabled:
            if key in self._memory_store:
                value, _ = self._memory_store[key]
                self._memory_store[key] = (value, time.time() + seconds)
                return True
            return False
        result = await self._execute("EXPIRE", key, str(seconds))
        return bool(result)

    async def ttl(self, key: str) -> int:
        """Get time to live for key (-1 if no expiry, -2 if not exists)"""
        if not self._enabled:
            if key in self._memory_store:
                _, expires_at = self._memory_store[key]
                remaining = int(expires_at - time.time())
                return max(remaining, 0)
            return -2
        result = await self._execute("TTL", key)
        return int(result) if result is not None else -2

    # -------------------------------------------------------------------------
    # Counter Operations (for rate limiting)
    # -------------------------------------------------------------------------

    async def incr(self, key: str) -> int:
        """Increment counter by 1"""
        if not self._enabled:
            if key in self._memory_store:
                value, expires_at = self._memory_store[key]
                if expires_at > time.time():
                    new_value = int(value) + 1
                    self._memory_store[key] = (str(new_value), expires_at)
                    return new_value
            self._memory_store[key] = ("1", time.time() + 60)
            return 1

        result = await self._execute("INCR", key)
        return int(result) if result else 0

    async def incrby(self, key: str, amount: int) -> int:
        """Increment counter by amount"""
        if not self._enabled:
            if key in self._memory_store:
                value, expires_at = self._memory_store[key]
                if expires_at > time.time():
                    new_value = int(value) + amount
                    self._memory_store[key] = (str(new_value), expires_at)
                    return new_value
            self._memory_store[key] = (str(amount), time.time() + 60)
            return amount

        result = await self._execute("INCRBY", key, str(amount))
        return int(result) if result else 0

    async def decr(self, key: str) -> int:
        """Decrement counter by 1"""
        if not self._enabled:
            if key in self._memory_store:
                value, expires_at = self._memory_store[key]
                if expires_at > time.time():
                    new_value = max(0, int(value) - 1)
                    self._memory_store[key] = (str(new_value), expires_at)
                    return new_value
            return 0

        result = await self._execute("DECR", key)
        return int(result) if result else 0

    # -------------------------------------------------------------------------
    # Hash Operations
    # -------------------------------------------------------------------------

    async def hget(self, key: str, field: str) -> Optional[str]:
        """Get hash field value"""
        if not self._enabled:
            hash_key = f"{key}:{field}"
            return await self.get(hash_key)
        return await self._execute("HGET", key, field)

    async def hset(self, key: str, field: str, value: str) -> int:
        """Set hash field value"""
        if not self._enabled:
            hash_key = f"{key}:{field}"
            await self.set(hash_key, value)
            return 1
        result = await self._execute("HSET", key, field, value)
        return int(result) if result else 0

    async def hdel(self, key: str, field: str) -> int:
        """Delete hash field"""
        if not self._enabled:
            hash_key = f"{key}:{field}"
            return await self.delete(hash_key)
        result = await self._execute("HDEL", key, field)
        return int(result) if result else 0

    async def hgetall(self, key: str) -> dict:
        """Get all hash fields and values"""
        if not self._enabled:
            return {}
        result = await self._execute("HGETALL", key)
        if result and isinstance(result, list):
            return dict(zip(result[::2], result[1::2]))
        return {}

    # -------------------------------------------------------------------------
    # Set Operations (for token blacklist)
    # -------------------------------------------------------------------------

    async def sadd(self, key: str, *members: str) -> int:
        """Add members to set"""
        if not self._enabled:
            set_key = f"set:{key}"
            if set_key not in self._memory_store:
                self._memory_store[set_key] = (set(), time.time() + 86400)
            existing_set, expires_at = self._memory_store[set_key]
            if isinstance(existing_set, set):
                before = len(existing_set)
                existing_set.update(members)
                self._memory_store[set_key] = (existing_set, expires_at)
                return len(existing_set) - before
            return 0

        result = await self._execute("SADD", key, *members)
        return int(result) if result else 0

    async def sismember(self, key: str, member: str) -> bool:
        """Check if member exists in set"""
        if not self._enabled:
            set_key = f"set:{key}"
            if set_key in self._memory_store:
                existing_set, expires_at = self._memory_store[set_key]
                if isinstance(existing_set, set) and expires_at > time.time():
                    return member in existing_set
            return False

        result = await self._execute("SISMEMBER", key, member)
        return bool(result)

    async def srem(self, key: str, *members: str) -> int:
        """Remove members from set"""
        if not self._enabled:
            set_key = f"set:{key}"
            if set_key in self._memory_store:
                existing_set, expires_at = self._memory_store[set_key]
                if isinstance(existing_set, set):
                    before = len(existing_set)
                    existing_set.difference_update(members)
                    self._memory_store[set_key] = (existing_set, expires_at)
                    return before - len(existing_set)
            return 0

        result = await self._execute("SREM", key, *members)
        return int(result) if result else 0

    # -------------------------------------------------------------------------
    # Rate Limiting Helpers
    # -------------------------------------------------------------------------

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, int, int]:
        """
        Check and update rate limit

        Returns:
            tuple of (allowed, current_count, remaining)
        """
        full_key = f"ratelimit:{key}"

        # Increment counter
        current = await self.incr(full_key)

        # Set expiry on first request
        if current == 1:
            await self.expire(full_key, window_seconds)

        allowed = current <= limit
        remaining = max(0, limit - current)

        return allowed, current, remaining

    # -------------------------------------------------------------------------
    # JSON Operations (convenience methods)
    # -------------------------------------------------------------------------

    async def get_json(self, key: str) -> Optional[Any]:
        """Get and parse JSON value"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set_json(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set JSON value"""
        try:
            serialized = json.dumps(value)
            return await self.set(key, serialized, ex=ex)
        except (TypeError, json.JSONEncodeError):
            logger.warning(f"Failed to serialize value for key {key}")
            return False

    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    async def close(self):
        """Close HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def cleanup_memory(self):
        """Cleanup expired in-memory entries"""
        if not self._enabled:
            current_time = time.time()
            expired_keys = [
                k for k, (_, exp) in self._memory_store.items()
                if exp < current_time
            ]
            for k in expired_keys:
                del self._memory_store[k]

    async def ping(self) -> bool:
        """Check connection health"""
        if not self._enabled:
            return True  # Memory fallback always "works"
        result = await self._execute("PING")
        return result == "PONG"


# Global instance
upstash_redis = UpstashRedis()


# Sync wrapper for non-async contexts
class UpstashRedisSync:
    """
    Synchronous wrapper for UpstashRedis

    Use in non-async code paths (e.g., middleware)
    """

    def __init__(self, async_client: UpstashRedis):
        self._async_client = async_client
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop"""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def _run(self, coro):
        """Run coroutine synchronously"""
        loop = self._get_loop()
        if loop.is_running():
            # We're in an async context, create a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result(timeout=10)
        else:
            return loop.run_until_complete(coro)

    def get(self, key: str) -> Optional[str]:
        return self._run(self._async_client.get(key))

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        return self._run(self._async_client.set(key, value, ex=ex))

    def incr(self, key: str) -> int:
        return self._run(self._async_client.incr(key))

    def expire(self, key: str, seconds: int) -> bool:
        return self._run(self._async_client.expire(key, seconds))

    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, int, int]:
        return self._run(
            self._async_client.check_rate_limit(key, limit, window_seconds)
        )


# Sync instance for middleware
upstash_redis_sync = UpstashRedisSync(upstash_redis)


__all__ = [
    "UpstashRedis",
    "UpstashRedisSync",
    "upstash_redis",
    "upstash_redis_sync",
]
