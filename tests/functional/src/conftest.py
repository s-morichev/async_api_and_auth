import asyncio
import json
from pathlib import Path

import aiohttp
import pytest
import pytest_asyncio
import redis.asyncio as aioredis
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from .settings import settings
from .utils.core_model import CoreModel


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def es_client():
    client = AsyncElasticsearch(settings.ES_URI)
    yield client

    await client.close()


@pytest_asyncio.fixture(scope="session")
async def redis_client() -> aioredis.Redis:
    client = await aioredis.from_url(settings.REDIS_URI)
    yield client
    await client.connection_pool.disconnect()
    await client.close()


@pytest_asyncio.fixture(scope="session")
async def aiohttp_session():
    session = aiohttp.ClientSession()
    yield session

    await session.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_es_indices(es_client: AsyncElasticsearch):
    """Запускается один раз на все тесты автоматически"""

    await es_client.options(ignore_status=[400, 404]).indices.delete(index=settings.ES_ALL_INDICES)

    # создаем индексы по списку. В /testdata должны лежать файлы json со схемами
    path = Path(__file__).parent / "testdata/"
    for index in settings.ES_ALL_INDICES:
        with open(path / f"{index}_schema.json", "r") as json_file:
            print(f"create index {index}")
            schema = json.loads(json_file.read())
            await es_client.indices.create(
                index=index,
                settings=schema.get("settings"),
                mappings=schema.get("mappings"),
            )
            await es_client.indices.refresh()


async def clear_es_indices(es_client: AsyncElasticsearch):
    await es_client.delete_by_query(index=settings.ES_ALL_INDICES, query={"match_all": {}})
    # обязательно, или будет conflict error
    await es_client.indices.refresh()


async def clear_redis(redis_client: aioredis.Redis):
    await redis_client.flushall()


@pytest_asyncio.fixture  # пришлось делать и фикстуру и функцию, иначе по scope конфликты шли c flush_data
async def clear_indices(es_client: AsyncElasticsearch):
    await clear_es_indices(es_client)


@pytest_asyncio.fixture(scope="module", autouse=True)
async def flush_data(es_client: AsyncElasticsearch, redis_client: aioredis.Redis):
    """Запускается на каждый модуль автоматически"""
    await clear_es_indices(es_client)
    await clear_redis(redis_client)


@pytest.fixture(scope="session")
def es_write_data(es_client):
    async def inner(documents: list[CoreModel], index: str, exclude: set[str], id_key: str = "id"):
        def make_action(index: str, document: CoreModel, id_key: str, exclude: set[str]):
            return {"_index": index, "_id": getattr(document, id_key), "_source": document.dict(exclude=exclude)}

        docs = [make_action(index, doc, id_key, exclude) for doc in documents]

        loaded, errors = await async_bulk(client=es_client, actions=docs)

        if errors:
            raise Exception("Ошибка записи данных в Elasticsearch")

        await es_client.indices.refresh()
        return loaded

    return inner


@pytest.fixture(scope="session")
def make_get_request(aiohttp_session):
    async def inner(path: str, query_data: dict | None = None, access_token: str | None = None):
        url = settings.BACKEND_URI + path
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        async with aiohttp_session.get(url, params=query_data, headers={"X-Request-Id": "test id"}) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return body, headers, status

    return inner
