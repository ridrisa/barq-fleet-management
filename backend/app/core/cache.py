"""
Multi-Level Caching Layer
Redis + In-Memory caching with cache warming, invalidation, and decorators
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from datetime import timedelta
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union

try:
    import redis
    from redis.connection import ConnectionPool

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None  # type: ignore
    ConnectionPool = None  # type: ignore

from app.core.performance_config import performance_config

logger = logging.getLogger(__name__)

T = TypeVar("T")


class InMemoryCache:
    """
    Simple in-memory LRU cache (Level 1)
    Fast but limited capacity
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 60):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: dict[str, tuple[Any, float]] = {}
        self._access_order: list[str] = []

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        import time

        if key in self._cache:
            value, expires_at = self._cache[key]

            # Check expiration
            if expires_at > time.time():
                # Update access order (LRU)
                if key in self._access_order:
                    self._access_order.remove(key)
                self._access_order.append(key)
                return value
            else:
                # Expired, remove
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        import time

        if ttl is None:
            ttl = self.default_ttl

        # Check capacity and evict if needed (LRU)
        if len(self._cache) >= self.max_size and key not in self._cache:
            if self._access_order:
                oldest_key = self._access_order.pop(0)
                del self._cache[oldest_key]

        expires_at = time.time() + ttl
        self._cache[key] = (value, expires_at)

        # Update access order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def delete(self, key: str) -> None:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_order:
            self._access_order.remove(key)

    def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
        self._access_order.clear()

    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "utilization": len(self._cache) / self.max_size if self.max_size > 0 else 0,
        }


class RedisCache:
    """
    Redis cache implementation (Level 2)
    Distributed and persistent
    """

    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._pool: Optional[ConnectionPool] = None
        self._connected = False

    def _connect(self) -> None:
        """Establish Redis connection"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, caching will be disabled")
            return

        if self._connected:
            return

        try:
            config = performance_config.cache

            self._pool = ConnectionPool.from_url(
                config.redis_url,
                max_connections=config.redis_max_connections,
                socket_timeout=config.redis_socket_timeout,
                socket_connect_timeout=config.redis_socket_connect_timeout,
                decode_responses=True,
            )

            self._client = redis.Redis(connection_pool=self._pool)

            # Test connection
            self._client.ping()
            self._connected = True
            logger.info("Redis cache connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False
            self._client = None

    @property
    def client(self) -> Optional[redis.Redis]:
        """Get Redis client, connecting if needed"""
        if not self._connected:
            self._connect()
        return self._client

    def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        if not self.client:
            return None

        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value in Redis with optional TTL"""
        if not self.client:
            return False

        try:
            if ttl:
                return bool(self.client.setex(key, ttl, value))
            else:
                return bool(self.client.set(key, value))
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.client:
            return False

        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if not self.client:
            return False

        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on existing key"""
        if not self.client:
            return False

        try:
            return bool(self.client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.client:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis DELETE pattern error for {pattern}: {e}")
            return 0

    def get_stats(self) -> dict:
        """Get Redis statistics"""
        if not self.client:
            return {"connected": False}

        try:
            info = self.client.info("stats")
            return {
                "connected": True,
                "total_connections": info.get("total_connections_received", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0), info.get("keyspace_misses", 0)
                ),
            }
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
            return {"connected": False, "error": str(e)}

    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate"""
        total = hits + misses
        return hits / total if total > 0 else 0.0

    def close(self) -> None:
        """Close Redis connection"""
        if self._client:
            self._client.close()
        if self._pool:
            self._pool.disconnect()
        self._connected = False
        logger.info("Redis connection closed")


class CacheManager:
    """
    Multi-level cache manager (L1: Memory, L2: Redis)
    Provides unified interface for caching operations
    """

    def __init__(self):
        config = performance_config.cache

        # Level 1: In-memory cache
        self.memory_cache = (
            InMemoryCache(max_size=config.memory_cache_size, default_ttl=config.memory_cache_ttl)
            if config.enable_memory_cache
            else None
        )

        # Level 2: Redis cache
        self.redis_cache = RedisCache()

        # Cache hit/miss tracking
        self._hits = 0
        self._misses = 0

        logger.info(
            f"Cache manager initialized: "
            f"memory_cache={'enabled' if self.memory_cache else 'disabled'}, "
            f"redis_cache=pending_connection"
        )

    def _make_key(self, namespace: str, key: str) -> str:
        """Create namespaced cache key"""
        return f"{namespace}:{key}"

    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Get value from cache (checks L1 then L2)

        Args:
            namespace: Cache namespace (e.g., 'user', 'organization')
            key: Cache key

        Returns:
            Cached value or None
        """
        cache_key = self._make_key(namespace, key)

        # Try L1 (memory) first
        if self.memory_cache:
            value = self.memory_cache.get(cache_key)
            if value is not None:
                self._hits += 1
                logger.debug(f"Cache hit (L1): {cache_key}")
                return value

        # Try L2 (Redis)
        redis_value = self.redis_cache.get(cache_key)
        if redis_value is not None:
            self._hits += 1
            logger.debug(f"Cache hit (L2): {cache_key}")

            # Deserialize
            try:
                value = json.loads(redis_value)

                # Populate L1 cache
                if self.memory_cache:
                    self.memory_cache.set(cache_key, value)

                return value
            except json.JSONDecodeError:
                # Return as string if not JSON
                return redis_value

        # Cache miss
        self._misses += 1
        logger.debug(f"Cache miss: {cache_key}")
        return None

    def set(self, namespace: str, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache (both L1 and L2)

        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        cache_key = self._make_key(namespace, key)

        # Set in L1 (memory)
        if self.memory_cache:
            memory_ttl = ttl or performance_config.cache.memory_cache_ttl
            self.memory_cache.set(cache_key, value, memory_ttl)

        # Set in L2 (Redis)
        try:
            serialized = json.dumps(value)
            redis_ttl = ttl or performance_config.cache.default_ttl
            self.redis_cache.set(cache_key, serialized, redis_ttl)
            logger.debug(f"Cache set: {cache_key} (ttl={redis_ttl}s)")
        except (TypeError, json.JSONEncodeError) as e:
            logger.warning(f"Failed to serialize cache value for {cache_key}: {e}")

    def delete(self, namespace: str, key: str) -> None:
        """
        Delete key from cache (both L1 and L2)

        Args:
            namespace: Cache namespace
            key: Cache key
        """
        cache_key = self._make_key(namespace, key)

        if self.memory_cache:
            self.memory_cache.delete(cache_key)

        self.redis_cache.delete(cache_key)
        logger.debug(f"Cache deleted: {cache_key}")

    def delete_pattern(self, namespace: str, pattern: str = "*") -> None:
        """
        Delete all keys matching pattern in namespace

        Args:
            namespace: Cache namespace
            pattern: Key pattern (supports wildcards)
        """
        full_pattern = self._make_key(namespace, pattern)

        # Clear L1 (memory) - requires full clear as we don't track patterns
        if self.memory_cache and pattern == "*":
            self.memory_cache.clear()

        # Clear L2 (Redis) with pattern matching
        deleted_count = self.redis_cache.delete_pattern(full_pattern)
        logger.info(f"Cache invalidated: {full_pattern} ({deleted_count} keys)")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        stats = {
            "hit_rate": hit_rate,
            "total_hits": self._hits,
            "total_misses": self._misses,
            "total_requests": total_requests,
        }

        if self.memory_cache:
            stats["memory_cache"] = self.memory_cache.get_stats()

        stats["redis_cache"] = self.redis_cache.get_stats()

        return stats

    def close(self) -> None:
        """Close cache connections"""
        self.redis_cache.close()
        if self.memory_cache:
            self.memory_cache.clear()


# Global cache manager instance
cache_manager = CacheManager()


# Cache decorators
def cached(
    namespace: str, ttl: Optional[int] = None, key_func: Optional[Callable[..., str]] = None
):
    """
    Decorator to cache function results

    Args:
        namespace: Cache namespace
        ttl: Cache TTL in seconds
        key_func: Function to generate cache key from args

    Usage:
        @cached(namespace="users", ttl=300)
        def get_user(user_id: str):
            return db.query(User).filter(User.id == user_id).first()

        @cached(namespace="users", key_func=lambda user_id: f"user_{user_id}")
        def get_user(user_id: str):
            return db.query(User).filter(User.id == user_id).first()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: hash function name and arguments
                key_parts = [func.__name__] + [str(arg) for arg in args]
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                key_string = "|".join(key_parts)
                cache_key = hashlib.md5(key_string.encode()).hexdigest()

            # Try to get from cache
            cached_value = cache_manager.get(namespace, cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(namespace, cache_key, result, ttl)

            return result

        return wrapper

    return decorator


def invalidate_cache(namespace: str, pattern: str = "*"):
    """
    Invalidate cache entries matching pattern

    Usage:
        invalidate_cache("users", "user_123")
        invalidate_cache("organizations", "*")  # Clear all org cache
    """
    cache_manager.delete_pattern(namespace, pattern)


# Export commonly used items
__all__ = [
    "cache_manager",
    "cached",
    "invalidate_cache",
    "InMemoryCache",
    "RedisCache",
    "CacheManager",
]
