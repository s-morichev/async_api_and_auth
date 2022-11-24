import aioredis
from api.v1 import films
from core import config
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from db import elastic, redis

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = aioredis.Redis(connection_pool=aioredis.ConnectionPool.from_url(config.REDIS_DSN))
    elastic.es = AsyncElasticsearch(hosts=config.ELK_DSN)


@app.on_event("shutdown")
async def shutdown():
    await elastic.es.close()


# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
