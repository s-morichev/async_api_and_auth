import logging
from abc import ABC, abstractmethod
from typing import Any
from aioredis import Redis, RedisError

from utils import hash_dict

logger = logging.getLogger(__name__)


class BaseCacheService(ABC):
    """Абстрактный класс для службы кэша"""

    @abstractmethod
    async def get(self, key: dict[str, int | str]) -> str:
        pass

    @abstractmethod
    async def put(self, key: dict[str, int | str], value: str, expire: int = 0) -> None:
        pass

    @abstractmethod
    async def ping(self) -> bool:
        """True if available"""


class RedisCacheService(BaseCacheService):
    redis: Redis

    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def _hash_key(key: dict[str, int | str], preffix: str = ''):
        return hash_dict(preffix, key)

    async def get(self, key: Any, preffix: str = '') -> Any:
        try:
            data = await self.redis.get(self._hash_key(key, preffix))
        except RedisError as err:
            logger.error(f"Error get from cache: {err}")
            data = None
        return data

    async def put(self, key: dict[str, int | str], value: str,  expire: int = 0, preffix: str = '') -> None:
        try:
            await self.redis.set(self._hash_key(key, preffix), value, ex=expire)
        except RedisError as err:
            logger.error(f"Error put to cache: {err}")

    async def ping(self):
        try:
            await self.redis.ping()
            return True
        except RedisError:
            logger.debug(f'No ping for redis:{self.redis}')
            return False
