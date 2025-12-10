"""
Redis-Based Distributed Rate Limiter

Production-grade rate limiting using Redis for distributed environments.
Supports multiple algorithms: fixed window, sliding window, and token bucket.

Features:
- Distributed rate limiting across multiple instances
- Multiple algorithm support
- Per-user, per-IP, and per-endpoint limiting
- Configurable limits and windows
- Automatic key expiration
- Rate limit headers support

Author: BARQ Security Team
Last Updated: 2025-12-10
"""

import time
import logging
from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import redis.asyncio as aioredis
    from redis.asyncio import Redis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import aioredis
        from aioredis import Redis
        REDIS_AVAILABLE = True
    except ImportError:
        REDIS_AVAILABLE = False
        Redis = None  # type: ignore

from app.core.performance_config import performance_config

logger = logging.getLogger(__name__)


class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithms"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    limit: int
    remaining: int
    reset_at: int  # Unix timestamp
    retry_after: Optional[int] = None  # Seconds until retry


class DistributedRateLimiter:
    """
    Redis-based distributed rate limiter for production environments.

    Usage:
        limiter = DistributedRateLimiter(redis_url="redis://localhost:6379")
        await limiter.connect()

        # Check rate limit
        result = await limiter.check_rate_limit(
            key="user:123",
            limit=100,
            window=60  # 100 requests per minute
        )

        if not result.allowed:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        key_prefix: str = "ratelimit",
        algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW,
    ):
        """
        Initialize rate limiter.

        Args:
            redis_url: Redis connection URL
            key_prefix: Prefix for all rate limit keys
            algorithm: Rate limiting algorithm to use
        """
        self.redis_url = redis_url or getattr(
            performance_config.cache, 'redis_url', 'redis://localhost:6379'
        )
        self.key_prefix = key_prefix
        self.algorithm = algorithm
        self._redis: Optional[Redis] = None
        self._connected = False

    async def connect(self) -> bool:
        """
        Establish Redis connection.

        Returns:
            True if connected successfully, False otherwise
        """
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available for rate limiting")
            return False

        if self._connected and self._redis:
            return True

        try:
            self._redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._redis.ping()
            self._connected = True
            logger.info("Rate limiter connected to Redis")
            return True
        except Exception as e:
            logger.error(f"Failed to connect rate limiter to Redis: {e}")
            self._connected = False
            return False

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._connected = False
            logger.info("Rate limiter disconnected from Redis")

    def _make_key(self, key: str) -> str:
        """Create full Redis key with prefix."""
        return f"{self.key_prefix}:{key}"

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int,
    ) -> RateLimitResult:
        """
        Check if request is within rate limit.

        Args:
            key: Unique identifier (user_id, ip, endpoint, etc.)
            limit: Maximum requests allowed in window
            window: Time window in seconds

        Returns:
            RateLimitResult with allowed status and metadata
        """
        if not self._connected or not self._redis:
            # Fallback: allow request if Redis unavailable
            logger.warning("Redis unavailable, allowing request")
            return RateLimitResult(
                allowed=True,
                limit=limit,
                remaining=limit,
                reset_at=int(time.time()) + window,
            )

        if self.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return await self._fixed_window(key, limit, window)
        elif self.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return await self._sliding_window(key, limit, window)
        elif self.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return await self._token_bucket(key, limit, window)
        else:
            return await self._sliding_window(key, limit, window)

    async def _fixed_window(
        self,
        key: str,
        limit: int,
        window: int,
    ) -> RateLimitResult:
        """
        Fixed window rate limiting.

        Simple counter that resets at fixed intervals.
        """
        redis_key = self._make_key(f"fw:{key}")
        now = int(time.time())
        window_start = (now // window) * window
        window_key = f"{redis_key}:{window_start}"

        try:
            pipe = self._redis.pipeline()
            pipe.incr(window_key)
            pipe.expire(window_key, window + 1)  # Extra second for safety
            results = await pipe.execute()

            current_count = results[0]
            remaining = max(0, limit - current_count)
            reset_at = window_start + window

            if current_count > limit:
                return RateLimitResult(
                    allowed=False,
                    limit=limit,
                    remaining=0,
                    reset_at=reset_at,
                    retry_after=reset_at - now,
                )

            return RateLimitResult(
                allowed=True,
                limit=limit,
                remaining=remaining,
                reset_at=reset_at,
            )
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return RateLimitResult(
                allowed=True,
                limit=limit,
                remaining=limit,
                reset_at=now + window,
            )

    async def _sliding_window(
        self,
        key: str,
        limit: int,
        window: int,
    ) -> RateLimitResult:
        """
        Sliding window rate limiting using sorted sets.

        More accurate than fixed window, prevents burst at window boundaries.
        """
        redis_key = self._make_key(f"sw:{key}")
        now = time.time()
        window_start = now - window

        try:
            pipe = self._redis.pipeline()
            # Remove old entries
            pipe.zremrangebyscore(redis_key, "-inf", window_start)
            # Add current request
            pipe.zadd(redis_key, {f"{now}": now})
            # Count requests in window
            pipe.zcard(redis_key)
            # Set expiration
            pipe.expire(redis_key, window + 1)
            results = await pipe.execute()

            current_count = results[2]
            remaining = max(0, limit - current_count)
            reset_at = int(now) + window

            if current_count > limit:
                # Get oldest entry to calculate retry time
                oldest = await self._redis.zrange(redis_key, 0, 0, withscores=True)
                if oldest:
                    retry_after = int(oldest[0][1] + window - now) + 1
                else:
                    retry_after = window

                return RateLimitResult(
                    allowed=False,
                    limit=limit,
                    remaining=0,
                    reset_at=reset_at,
                    retry_after=retry_after,
                )

            return RateLimitResult(
                allowed=True,
                limit=limit,
                remaining=remaining,
                reset_at=reset_at,
            )
        except Exception as e:
            logger.error(f"Sliding window rate limit check failed: {e}")
            return RateLimitResult(
                allowed=True,
                limit=limit,
                remaining=limit,
                reset_at=int(now) + window,
            )

    async def _token_bucket(
        self,
        key: str,
        limit: int,  # bucket capacity
        window: int,  # refill rate (tokens per second = limit/window)
    ) -> RateLimitResult:
        """
        Token bucket rate limiting.

        Allows bursts up to bucket capacity while maintaining average rate.
        """
        redis_key = self._make_key(f"tb:{key}")
        now = time.time()
        refill_rate = limit / window  # tokens per second

        # Lua script for atomic token bucket operation
        lua_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        local bucket = redis.call('HMGET', key, 'tokens', 'last_update')
        local tokens = tonumber(bucket[1]) or capacity
        local last_update = tonumber(bucket[2]) or now

        -- Calculate tokens to add based on time elapsed
        local elapsed = now - last_update
        local new_tokens = math.min(capacity, tokens + (elapsed * refill_rate))

        if new_tokens >= 1 then
            -- Consume a token
            new_tokens = new_tokens - 1
            redis.call('HMSET', key, 'tokens', new_tokens, 'last_update', now)
            redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) + 1)
            return {1, new_tokens}  -- allowed, remaining
        else
            -- No tokens available
            local wait_time = (1 - new_tokens) / refill_rate
            return {0, wait_time}  -- denied, wait time
        end
        """

        try:
            result = await self._redis.eval(
                lua_script,
                1,
                redis_key,
                limit,
                refill_rate,
                now,
            )

            allowed = result[0] == 1

            if allowed:
                return RateLimitResult(
                    allowed=True,
                    limit=limit,
                    remaining=int(result[1]),
                    reset_at=int(now) + window,
                )
            else:
                retry_after = int(result[1]) + 1
                return RateLimitResult(
                    allowed=False,
                    limit=limit,
                    remaining=0,
                    reset_at=int(now) + retry_after,
                    retry_after=retry_after,
                )
        except Exception as e:
            logger.error(f"Token bucket rate limit check failed: {e}")
            return RateLimitResult(
                allowed=True,
                limit=limit,
                remaining=limit,
                reset_at=int(now) + window,
            )

    async def reset(self, key: str) -> bool:
        """
        Reset rate limit for a key.

        Args:
            key: Rate limit key to reset

        Returns:
            True if reset successfully
        """
        if not self._redis:
            return False

        try:
            patterns = [
                self._make_key(f"fw:{key}:*"),
                self._make_key(f"sw:{key}"),
                self._make_key(f"tb:{key}"),
            ]

            for pattern in patterns:
                keys = await self._redis.keys(pattern)
                if keys:
                    await self._redis.delete(*keys)

            return True
        except Exception as e:
            logger.error(f"Failed to reset rate limit for {key}: {e}")
            return False

    async def get_usage(self, key: str, window: int) -> Tuple[int, int]:
        """
        Get current usage for a key.

        Args:
            key: Rate limit key
            window: Time window in seconds

        Returns:
            Tuple of (current_count, window_remaining_seconds)
        """
        if not self._redis:
            return (0, window)

        redis_key = self._make_key(f"sw:{key}")
        now = time.time()
        window_start = now - window

        try:
            # Count entries in current window
            count = await self._redis.zcount(redis_key, window_start, now)
            return (count, int(window - (now % window)))
        except Exception as e:
            logger.error(f"Failed to get rate limit usage for {key}: {e}")
            return (0, window)


# Global rate limiter instance
_rate_limiter: Optional[DistributedRateLimiter] = None


async def get_rate_limiter() -> DistributedRateLimiter:
    """
    Get or create global rate limiter instance.

    Returns:
        DistributedRateLimiter instance
    """
    global _rate_limiter

    if _rate_limiter is None:
        _rate_limiter = DistributedRateLimiter()
        await _rate_limiter.connect()

    return _rate_limiter


async def close_rate_limiter() -> None:
    """Close global rate limiter connection."""
    global _rate_limiter

    if _rate_limiter:
        await _rate_limiter.disconnect()
        _rate_limiter = None


# Convenience functions for common rate limit scenarios
async def check_user_rate_limit(
    user_id: int,
    limit: int = 100,
    window: int = 60,
) -> RateLimitResult:
    """Check rate limit for authenticated user."""
    limiter = await get_rate_limiter()
    return await limiter.check_rate_limit(f"user:{user_id}", limit, window)


async def check_ip_rate_limit(
    ip_address: str,
    limit: int = 50,
    window: int = 60,
) -> RateLimitResult:
    """Check rate limit for IP address."""
    limiter = await get_rate_limiter()
    return await limiter.check_rate_limit(f"ip:{ip_address}", limit, window)


async def check_endpoint_rate_limit(
    endpoint: str,
    identifier: str,
    limit: int = 100,
    window: int = 60,
) -> RateLimitResult:
    """Check rate limit for specific endpoint."""
    limiter = await get_rate_limiter()
    return await limiter.check_rate_limit(f"endpoint:{endpoint}:{identifier}", limit, window)


async def check_login_rate_limit(
    identifier: str,
    limit: int = 5,
    window: int = 300,  # 5 attempts per 5 minutes
) -> RateLimitResult:
    """Check rate limit for login attempts."""
    limiter = await get_rate_limiter()
    return await limiter.check_rate_limit(f"login:{identifier}", limit, window)


async def check_password_reset_rate_limit(
    email: str,
    limit: int = 3,
    window: int = 3600,  # 3 attempts per hour
) -> RateLimitResult:
    """Check rate limit for password reset requests."""
    limiter = await get_rate_limiter()
    return await limiter.check_rate_limit(f"pwd_reset:{email}", limit, window)


__all__ = [
    "DistributedRateLimiter",
    "RateLimitResult",
    "RateLimitAlgorithm",
    "get_rate_limiter",
    "close_rate_limiter",
    "check_user_rate_limit",
    "check_ip_rate_limit",
    "check_endpoint_rate_limit",
    "check_login_rate_limit",
    "check_password_reset_rate_limit",
]
