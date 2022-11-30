import logging

import aioredis
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import films_by_person, genre_by_id, genres_all, person_by_id, person_search
from core import config
from core.logger import LOGGING
from db import elastic, redis

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    # Подключаемся к базам при старте сервера
    # Подключиться можем при работающем event-loop
    # Поэтому логика подключения происходит в асинхронной функции
    # redis.redis = await aioredis.create_redis_pool(
    #     (config.REDIS_HOST, config.REDIS_PORT), password="123qwe", minsize=10, maxsize=20
    # )
    redis.redis = await aioredis.from_url(f"redis://default:123qwe@{config.REDIS_HOST}:{config.REDIS_PORT}")
    elastic.es = AsyncElasticsearch(hosts=[f"http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"])


@app.on_event("shutdown")
async def shutdown():
    # Отключаемся от баз при выключении сервера
    await redis.redis.close()
    await elastic.es.close()


app.include_router(films_by_person.router, prefix="/api/v1/persons", tags=["films_by_person"])
app.include_router(person_by_id.router, prefix="/api/v1/persons", tags=["person_id"])
app.include_router(person_search.router, prefix="/api/v1/persons/search", tags=["person_search"])

app.include_router(genres_all.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(genre_by_id.router, prefix="/api/v1/genres", tags=["genre_id"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
