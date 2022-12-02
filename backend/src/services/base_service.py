from typing import Type

from aioredis import Redis
from core.service_logger import get_logger
from core.singletone import Singleton
from core.utils import classproperty, hash_dict, restrict_pages
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from models.base_dto import BaseDTO
from models.service_result import ServiceResult

logger = get_logger(__name__)


# ------------------------------------------------------------------------------ #
class BaseService(metaclass=Singleton):
    """
    Базовый класс для всех сервисов. Сделан как синглтон
    Надо только определить NAME,  BASE_MODEL, IS_LIST_RESULT
    и метод get_from_elastic()
    в словаре query_dict в методе get() ждем все параметры
    свойство RESPONSE_MODEL возвращает модель ответа, удобно в
    @router.get("/", response_model=Service.RESPONSE_MODEL)
    """

    USE_CACHE = True  # использовать ли кэш
    NAME = "BASE"  # имя сервиса. Используется в ключе редиса
    BASE_MODEL: Type[BaseDTO]  # базовый класс для ответа
    CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
    RESULT_MODEL: Type[ServiceResult]

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    def get_redis_key(self, keys: dict):
        return hash_dict(self.NAME, keys)

    async def get(self, **kwargs) -> ServiceResult | None:
        # 1. try to get data from cache
        if result := await self.get_from_cache(kwargs):
            result.cached = 1
            return result  #

        # 2. try to get data from es
        elif result := await self.get_from_elastic(**kwargs):
            await self.put_to_cache(kwargs, result)
            logger.debug(f"get from ES: {result}")
            return result
        else:
            logger.debug("Nothing find")
            return None

    async def get_from_elastic(self, **kwargs) -> ServiceResult | None:
        pass

    async def get_from_cache(self, query_dict: dict) -> ServiceResult | None:
        if not self.USE_CACHE:
            return None

        key = self.get_redis_key(query_dict)
        data = await self.redis.get(key)
        if not data:
            return None
        logger.debug(f"get from cache key: {key}")
        result = self.RESULT_MODEL.parse_raw(data)
        return result

    async def put_to_cache(self, query_dict: dict, result: ServiceResult) -> None:
        if not self.USE_CACHE:
            return

        key = self.get_redis_key(query_dict)
        await self.redis.set(key, result.json(), ex=self.CACHE_EXPIRE_IN_SECONDS)
        logger.debug(f"save to cache key: {key}")

    @classmethod
    async def get_service(cls: Type["BaseService"]) -> "BaseService":
        """return instance of Service and its must be the same, its a SINGLETONE!!!"""
        redis = await get_redis()
        elastic = await get_elastic()
        return cls(redis, elastic)

    # ------------------------------------------------------------------------------ #
