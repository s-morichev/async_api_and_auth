from typing import Type
import logging
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from aioredis.exceptions import RedisError

from core.constants import DEFAULT_CACHE_EXPIRE_IN_SECONDS
from core.singletone import Singleton
from core.utils import classproperty, hash_dict
from db.elastic import get_elastic
from db.redis import get_redis
from models.service_result import ServiceListResult, ServiceSingeResult

logger = logging.getLogger(__name__)

MaybeResult = ServiceSingeResult | ServiceListResult | None


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
    CACHE_EXPIRE_IN_SECONDS = DEFAULT_CACHE_EXPIRE_IN_SECONDS
    RESULT_MODEL: ServiceSingeResult | ServiceListResult

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    @classproperty
    def BASE_MODEL(self):
        """return base model from Result_model"""
        return self.RESULT_MODEL.__fields__["result"].type_

    def get_redis_key(self, keys: dict):
        return hash_dict(self.NAME, keys)

    async def get(self, **kwargs) -> MaybeResult:
        # 1. try to get data from cache
        if result := await self.get_from_cache(kwargs):
            result.cached = 1
            return result

        # 2. try to get data from es
        elif result := await self.get_from_elastic(**kwargs):
            logger.debug(f"get from ES: {result}")
            await self.put_to_cache(kwargs, result)
            return result
        else:
            logger.debug("Nothing find")
            return None

    async def get_from_elastic(self, **kwargs) -> MaybeResult:
        pass

    async def get_from_cache(self, query_dict: dict) -> MaybeResult:
        if not self.USE_CACHE:
            return None

        key = self.get_redis_key(query_dict)
        try:
            data = await self.redis.get(key)
        except RedisError as err:
            logger.error(f"Error get from cache: {err}")
            data = None

        if not data:
            return None
        logger.debug(f"get from cache key: {key}")
        result = self.RESULT_MODEL.parse_raw(data)
        return result

    async def put_to_cache(self, query_dict: dict, result: ServiceSingeResult | ServiceListResult) -> None:
        if not self.USE_CACHE:
            return

        key = self.get_redis_key(query_dict)
        logger.debug(f"save to cache key: {key}")

        try:
            await self.redis.set(key, result.json(), ex=self.CACHE_EXPIRE_IN_SECONDS)
        except RedisError as err:
            logger.error(f"Error put to cache: {err}")


    @classmethod
    async def get_service(cls: Type["BaseService"]) -> "BaseService":
        """return instance of Service and its must be the same, its a SINGLETONE!!!"""
        redis = await get_redis()
        elastic = await get_elastic()
        return cls(redis, elastic)

    # ------------------------------------------------------------------------------ #
