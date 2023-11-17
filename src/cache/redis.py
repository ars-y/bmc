import json
from typing import Any, Optional

from aioredis import Redis, from_url

from src import main
from src.core.settings.base import settings


class RedisClient:

    @staticmethod
    async def init_redis() -> Redis:
        """Initialize Redis client."""
        return from_url(str(settings.REDIS_URL))

    @staticmethod
    async def set_cache(
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> None:
        """Set key to hold the string value."""
        await main.app.state.redis.set(key, json.dumps(value), expire)

    @staticmethod
    async def get_cache(key: str) -> Any:
        """Get the value of key."""
        value: Optional[Any] = await main.app.state.redis.get(key)
        if value:
            return json.loads(value)

    @staticmethod
    async def add_values_to_key(key: str, *values) -> None:
        """Add the specified members to the set stored at key."""
        await main.app.state.redis.sadd(key, *values)

    @staticmethod
    async def set_expire(key: str, seconds: int) -> None:
        """Set a timeout on key."""
        await main.app.state.redis.expire(key, seconds)

    @staticmethod
    async def get_values_from_key(key: str) -> set[bytes]:
        """Returns all the members of the set value stored at key."""
        return await main.app.state.redis.smembers(key)

    @staticmethod
    async def remove(*keys) -> None:
        """Removes the specified keys. A key is ignored if it does not exist"""
        await main.app.state.redis.delete(*keys)
