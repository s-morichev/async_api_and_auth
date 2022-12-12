import logging
from abc import ABC, abstractmethod
from typing import Any
from aioredis import Redis, RedisError

from core.singletone import Singleton
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
    __metaclass__ = Singleton

    redis: Redis

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> str:
        try:
            data = await self.redis.get(key)
        except RedisError as err:
            logger.error(f"Error get from cache: {err}")
            data = None
        return data

    async def put(self, key: str, value: str,  expire: int = 0) -> None:
        try:
            await self.redis.set(key, value, ex=expire)
        except RedisError as err:
            logger.error(f"Error put to cache: {err}")

    async def ping(self):
        try:
            await self.redis.ping()
            return True
        except RedisError:
            logger.debug(f'No ping for redis:{self.redis}')
            return False
