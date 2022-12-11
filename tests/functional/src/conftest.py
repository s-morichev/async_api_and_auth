import asyncio
from typing import Any, Iterator
import json

import redis.asyncio as aioredis
import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from pathlib import Path

from .settings import settings
from .testdata.core_model import CoreModel


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


@pytest_asyncio.fixture(scope='session')
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

    # удаляем индексы на всякий случай - а надо? Игнорируем ошибки если индексов нет
    # удаляем - вдруг схема поменялась?
    await es_client.options(ignore_status=[400, 404]).indices.delete(index=settings.ES_ALL_INDICES)

    # создаем индексы по списку. В /testdata должны лежать файлы json со схемами
    path = Path(__file__).parent / 'testdata/'
    for index in settings.ES_ALL_INDICES:
        with open(path / f'{index}_schema.json', 'r') as json_file:
            print(f'create index {index}')
            schema = json.loads(json_file.read())
            await es_client.indices.create(
                index=index,
                settings=schema.get("settings"),
                mappings=schema.get("mappings"),
            )
            await es_client.indices.refresh()


@pytest_asyncio.fixture(scope='module', autouse=True)
async def flush_data(es_client: AsyncElasticsearch, redis_client: aioredis.Redis):
#async def flush_data(es_client: AsyncElasticsearch):
    """ Запускается на каждый модуль автоматически """

    async def clear_redis():
        await redis_client.flushall()

    async def clear_es_indices():
        await es_client.delete_by_query(
            index=settings.ES_ALL_INDICES,
            query={"match_all": {}},
        )

    await clear_redis()
    await clear_es_indices()


@pytest.fixture(scope='session')
def es_write_data(es_client):
    async def inner(documents: list[CoreModel], index: str, id_key: str = 'id', exclude: set[str] = {'id'}):
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
    async def inner(path: str, query_data: dict | None = None):
        url = settings.API_URI + path
        async with aiohttp_session.get(url, params=query_data) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return body, headers, status

    return inner
