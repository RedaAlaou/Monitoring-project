"""
Redis Cache Service for Device Management.
Provides caching functionality for device lists and other data.
"""

import json
import redis
from typing import Optional, List, Any
from helpers.config import REDIS_HOST, REDIS_PORT, REDIS_DB, logger


class CacheService:
    """Redis-based caching service for device data."""

    def __init__(self):
        """Initialize Redis connection."""
        self._client: Optional[redis.Redis] = None

    @property
    def client(self) -> redis.Redis:
        """Lazy initialization of Redis client."""
        if self._client is None:
            try:
                self._client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    decode_responses=True
                )
                # Test connection
                self._client.ping()
                logger.info(f"Redis connected: {REDIS_HOST}:{REDIS_PORT}")
            except redis.ConnectionError as e:
                logger.error(f"Redis connection failed: {e}")
                raise
        return self._client

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, expire_seconds: int = 300) -> bool:
        """Set value in cache with expiration."""
        try:
            serialized = json.dumps(value)
            return self.client.setex(key, expire_seconds, serialized)
        except (redis.RedisError, TypeError) as e:
            logger.error(f"Redis set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            return bool(self.client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except redis.RedisError as e:
            logger.error(f"Redis delete pattern error: {e}")
            return 0

    # Device-specific cache methods

    def get_devices_cache(self) -> Optional[List[dict]]:
        """Get cached device list."""
        cached = self.get("devices:all")
        if cached:
            return json.loads(cached)
        return None

    def set_devices_cache(self, devices: List[dict], expire_seconds: int = 60) -> bool:
        """Cache device list."""
        return self.set("devices:all", devices, expire_seconds)

    def invalidate_devices_cache(self) -> int:
        """Invalidate all device-related cache entries."""
        return self.delete_pattern("devices:*")

    def get_device_cache(self, device_id: int) -> Optional[dict]:
        """Get cached single device."""
        cached = self.get(f"device:{device_id}")
        if cached:
            return json.loads(cached)
        return None

    def set_device_cache(self, device_id: int, device: dict, expire_seconds: int = 300) -> bool:
        """Cache single device."""
        return self.set(f"device:{device_id}", device, expire_seconds)

    def invalidate_device_cache(self, device_id: int) -> bool:
        """Invalidate single device cache."""
        return self.delete(f"device:{device_id}")


# Singleton instance
cache_service = CacheService()
