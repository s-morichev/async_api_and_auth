from typing import Type
from aioredis import Redis
from core.singletone import Singleton
from core.utils import classproperty, hash_dict, restrict_pages
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.base_dto import BaseDTO
from models.service_result import ServiceResult
from core.service_logger import get_logger


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
    BASE_MODEL: Type[BaseDTO] = BaseDTO  # базовый класс для ответа
    CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
    IS_LIST_RESULT = False  # одно значение в ответе или список ожидается
    # класс ответа, он определяется в зависимости от
    #  BASE_MODEL и IS_LIST_RESULT
    RESULT_MODEL: Type[ServiceResult]

    def __new__(cls, *args, **kwargs):
        """
        Дополняю классовый метод чтобы в рантайме определять класс ответа
        Извращаюсь как могу))
        """
        cls.init_result_model()
        return super().__new__(cls)

    @classmethod
    def init_result_model(cls) -> Type[ServiceResult]:

        class Result(ServiceResult):
            if cls.IS_LIST_RESULT:
                result: list[cls.BASE_MODEL]
            else:
                result: cls.BASE_MODEL

        # надо чтобы имена классов ответа были уникальны,
        # инача FastApi не сможет создать OpenAPI документацию
        Result.__name__ = f"Result:{cls.NAME}"
        cls.RESULT_MODEL = Result
        return Result

    @classproperty
    def RESPONSE_MODEL(cls):
        """Красивое свойство возвращает модель ответа. Нужно во роуте"""
        return cls.init_result_model()
        # return cls.RESULT_MODEL

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    def get_redis_key(self, keys: dict):
        return hash_dict(self.NAME, keys)

    async def get(self, query_dict: dict = None) -> ServiceResult | None:
        # ограничиваем параметры пагинации
        query_dict = restrict_pages(query_dict)

        # 1. try to get data from cache
        if result := await self.get_from_cache(query_dict):
            result.cached = 1
            return result  #

        # 2. try to get data from es
        elif result := await self.get_from_elastic(query_dict):
            await self.put_to_cache(query_dict, result)
            logger.debug(f'get from ES: {result}')
            return result
        else:
            logger.debug('Nothing find')
            return None

    async def get_from_elastic(self, query_dict: dict) -> ServiceResult | None:
        pass

    async def get_from_cache(self, query_dict: dict) -> ServiceResult | None:
        if not self.USE_CACHE:
            return None

        key = self.get_redis_key(query_dict)
        data = await self.redis.get(key)
        if not data:
            return None
        logger.debug(f'get from cache key: {key}')
        result = self.RESULT_MODEL.parse_raw(data)
        return result

    async def put_to_cache(self, query_dict: dict, result: ServiceResult) -> None:
        if not self.USE_CACHE:
            return

        key = self.get_redis_key(query_dict)
        await self.redis.set(key, result.json(), ex=self.CACHE_EXPIRE_IN_SECONDS)
        logger.debug(f'save to cache key: {key}')

    @classmethod
    def get_service(
            cls: Type["BaseService"], redis: Redis = Depends(get_redis),
            elastic: AsyncElasticsearch = Depends(get_elastic)
    ) -> "BaseService":
        """return instance of Service and its must be the same, its a SINGLETONE!!!"""
        return cls(redis, elastic)

    # ------------------------------------------------------------------------------ #
