import logging
from http import HTTPStatus
from typing import Type

from fastapi import Depends, HTTPException

from core.cache_service import BaseCacheService
from core.constants import DEFAULT_CACHE_EXPIRE_IN_SECONDS
from core.database_service import BaseDatabaseService
from core.exceptions import DatabaseConnectionError
from core.singletone import Singleton
from core.utils import classproperty, hash_dict
from db.elastic import get_es_database_service
from db.redis_ import get_redis
from models.service_result import ServiceListResult, ServiceSingeResult

logger = logging.getLogger(__name__)

MaybeResult = ServiceSingeResult | ServiceListResult | None


# ------------------------------------------------------------------------------ #
class BaseService(metaclass=Singleton):
    """
    Базовый класс для всех сервисов. Сделан как синглтон
    Надо только определить NAME, RESULT_MODEL
    и метод get_from_elastic()
    в словаре **kwargs в методе get() ждем все параметры
    """

    USE_CACHE = True  # использовать ли кэш
    NAME = "BASE"  # имя сервиса. Используется в ключе редиса
    CACHE_EXPIRE_IN_SECONDS = DEFAULT_CACHE_EXPIRE_IN_SECONDS
    RESULT_MODEL: ServiceSingeResult | ServiceListResult

    def __init__(self, cache: BaseCacheService, database: BaseDatabaseService):
        self.cache_service = cache
        self.database_service = database

    @classproperty
    def BASE_MODEL(self):
        """return base model from Result_model"""
        return self.RESULT_MODEL.__fields__["result"].type_

    def get_hash_key(self, keys: dict):
        return hash_dict(self.NAME, keys)

    async def get(self, **kwargs) -> MaybeResult:
        # 1. try to get data from cache
        if result := await self.get_from_cache(kwargs):
            result.cached = 1
            return result

        # 2. try to get data from es
        try:
            result = await self.get_from_database(**kwargs)
        except DatabaseConnectionError:
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail="Service is unavailable. Please try a few minutes later.",
            )

        if result:
            logger.debug(f"get from database: {result}")
            await self.put_to_cache(kwargs, result)
            return result
        else:
            logger.debug("Nothing find")
            return None

    async def get_from_database(self, **kwargs) -> MaybeResult:
        pass

    async def get_from_cache(self, query_dict: dict) -> MaybeResult:
        if not self.USE_CACHE:
            return None
        key = self.get_hash_key(query_dict)
        logger.debug(f"get from cache, key: {key}")
        data = await self.cache_service.get(key)
        if not data:
            return None

        result = self.RESULT_MODEL.parse_raw(data)
        return result

    async def put_to_cache(self, query_dict: dict, result: ServiceSingeResult | ServiceListResult) -> None:
        if not self.USE_CACHE:
            return

        key = self.get_hash_key(query_dict)
        logger.debug(f"save to cache, key: {key}")
        await self.cache_service.put(key, result.json(), self.CACHE_EXPIRE_IN_SECONDS)

    @classmethod
    async def get_service(
        cls: Type["BaseService"],
        cache: BaseCacheService = Depends(get_redis),
        database: BaseDatabaseService = Depends(get_es_database_service),
    ) -> "BaseService":
        """return instance of Service and its must be the same, its a SINGLETONE!!!"""

        return cls(cache, database)

    # ------------------------------------------------------------------------------ #
