import redis.asyncio as redis
from config import Settings
import logging
import fnmatch

_redis = None

logger = logging.getLogger("app")


class InMemoryStore:
    def __init__(self):
        self._store = {}

    async def keys(self, pattern="*"):
        return [k for k in self._store if fnmatch.fnmatch(k, pattern)]

    async def get(self, key):
        return self._store.get(key)

    async def set(self, key, value, ex=None):
        self._store[key] = value

    async def incr(self, key):
        val = int(self._store.get(key, 0)) + 1
        self._store[key] = val
        return val

    async def mget(self, *keys):
        return [self._store.get(k) for k in keys]

    async def flushdb(self):
        self._store.clear()

    async def flushall(self):
        self._store.clear()

    # Synchronous clear for testing fixtures
    def clear(self):
        self._store.clear()


async def get_redis():
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
