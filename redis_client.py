import redis.asyncio as redis
from config import Settings
import logging
import fnmatch
from typing import Optional, List, Any

_redis = None

logger = logging.getLogger("app")


class InMemoryStore:
    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    async def keys(self, pattern: str = "*") -> List[str]:
        return [k for k in self._store if fnmatch.fnmatch(k, pattern)]

    async def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> None:
        self._store[key] = value

    async def incr(self, key: str) -> int:
        val = int(self._store.get(key, 0)) + 1
        self._store[key] = val
        return val

    async def mget(self, *keys: str) -> List[Optional[str]]:
        return [self._store.get(k) for k in keys]

    async def flushdb(self) -> None:
        self._store.clear()

    async def flushall(self) -> None:
        self._store.clear()

    # Synchronous clear for testing fixtures
    def clear(self) -> None:
        self._store.clear()


async def get_redis() -> Any:
    global _redis
    settings = Settings()
    if settings.testing:
        if not isinstance(_redis, InMemoryStore):
            _redis = InMemoryStore()
        return _redis

    # production behavior
    if _redis is None:
        logger.debug("Creating new Redis connection")
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
        await _redis.ping()
    return _redis
