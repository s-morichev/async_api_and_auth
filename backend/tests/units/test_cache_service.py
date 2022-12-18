import pytest

from core.cache_service import RedisCacheService


class RedisMock:
    _mem: dict = {}
    enabled: bool = True

    async def set(self, key, value, ex=0):
        self._mem[key] = value

    async def get(self, key):
        if not self.enabled:
            return None
        return self._mem.get(key, None)

    async def ping(self):
        return self.enabled


@pytest.fixture(scope="session")
def redis_cache():
    client = RedisMock()
    cache = RedisCacheService(client)
    return cache, client


@pytest.mark.asyncio
async def test_put(redis_cache):
    cache, redis = redis_cache
    key = "11111"
    value1 = "{'test value': 'test'}"
    await cache.put(key, value1)
    value2 = await cache.get(key)
    assert value1 == value2
