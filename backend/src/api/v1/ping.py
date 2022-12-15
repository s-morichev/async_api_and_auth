import logging

from aioredis import Redis, RedisError
from db.elastic import get_es_database_service
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", summary="ping, answer-pong")
async def ping(redis: Redis = Depends(get_redis), elastic: AsyncElasticsearch = Depends(get_es_database_service)):

    elastic_ok = await elastic.ping()
    try:
        redis_ok = await redis.ping()
    except RedisError:
        redis_ok = False

    logger.debug(f"ping received, es:{elastic_ok} redis:{redis_ok}")
    return {"result": "pong", "base_service": elastic_ok, "cache_service": redis_ok}
