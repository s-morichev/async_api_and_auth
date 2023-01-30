from http import HTTPStatus
import logging

import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

import redis.asyncio as aioredis
from api.v1 import films, genres, persons, ping, view
from core.config import settings
from core.logger import LOGGING
from core.utils import configure_tracer
from db import elastic, redis_

tags_metadata = [
    {"name": "Фильмы", "description": "Запросы по фильмам"},
    {"name": "Персоны", "description": "Запросы по персонам"},
    {"name": "Жанры", "description": "Запросы по жанрам"},
]

logger = logging.getLogger(__name__)


async def require_header_request_id(x_request_id: str | None = Header(default=None)):
    if x_request_id is None:
        if app.debug:
            pass
        else:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="X-Request-Id header id is required")


deps = None
if settings.ENABLE_TRACER:
    deps = [Depends(require_header_request_id)]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    dependencies=deps,
)


@app.on_event("startup")
async def startup():
    logger.info("service start")
    redis_.redis = await aioredis.from_url(settings.REDIS_URI)
    elastic.es = AsyncElasticsearch(hosts=[settings.ES_URI])
    if settings.ENABLE_TRACER:
        configure_tracer()
        FastAPIInstrumentor.instrument_app(app)


@app.on_event("shutdown")
async def shutdown():
    # Отключаемся от баз при выключении сервера
    await redis_.redis.close()
    await elastic.es.close()
    logger.info("service shutdown")


app.include_router(ping.router, prefix="/api/v1/ping", tags=["Пинг"])
app.include_router(films.router, prefix="/api/v1/films", tags=["Фильмы"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["Персоны"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["Жанры"])
app.include_router(view.router, prefix="/api/v1/view", tags=["Просмотр"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
