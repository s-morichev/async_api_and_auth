import logging

import aioredis
import uvicorn as uvicorn
from api.v1 import persons, genres
from core.config import settings
from core.logger import LOGGING
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from db import elastic, redis

tags_metadata = [{"name": "Персоны", "description": "Участники фильма"},
                 {"name": "items", "description": "Manage items. So _fancy_ they have their own docs."}]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version='1.0.0',
    tags_metadata=tags_metadata,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():

    redis.redis = await aioredis.from_url(settings.REDIS_URI)
    elastic.es = AsyncElasticsearch(hosts=[settings.ES_URI])


@app.on_event("shutdown")
async def shutdown():
    # Отключаемся от баз при выключении сервера
    await redis.redis.close()
    await elastic.es.close()

app.include_router(persons.router, prefix="/api/v1/persons", tags=["Персоны"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["Жанры"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
