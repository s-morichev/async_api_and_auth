import asyncio
from typing import Any, Iterator
import json

import aioredis
import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from pathlib import Path

from settings import settings
# from src.testdata import genres_schema, movies_schema, persons_schema


def get_es_bulk_actions(documents: list[dict[str, Any]], index: str) -> Iterator[dict[str, Any]]:
    return ({"_index": index, "_id": document["id"], "_source": document} for document in documents)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
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

    await client.close()


@pytest_asyncio.fixture(scope="session")
async def aiohttp_session():
    session = aiohttp.ClientSession()
    yield session

    await session.close()


# @pytest_asyncio.fixture(scope="session", autouse=True)
# async def create_es_indices(es_client):
#     for index, schema in [
#         (settings.ES_MOVIES_INDEX, movies_schema),
#         (settings.ES_PERSONS_INDEX, persons_schema),
#         (settings.ES_GENRES_INDEX, genres_schema),
#     ]:
#         await es_client.indices.create(
#             index=index,
#             settings=schema.get("settings"),
#             mappings=schema.get("mappings"),
#         )

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_es_indices(es_client: AsyncElasticsearch):
    """Запускается один раз на все тесты автоматически"""

    # удаляем индексы на всякий случай - а надо?
    # можно не удалять, нужно проверить существование перед созданием индексов
    #await es_client.indices.delete(index=settings.ES_ALL_INDICES)

    # создаем индексы по списку. В /testdata должны лежать файлы json со схемами
    path = Path(__file__).parent / 'testdata/'
    for index in settings.ES_ALL_INDICES:
        if not await es_client.indices.exists(index=index):
            with open(path / f'{index}_schema.json', 'r') as json_file:
                print(f'create index {index}')
                schema = json.loads(json_file.read())
                await es_client.indices.create(
                    index=index,
                    settings=schema.get("settings"),
                    mappings=schema.get("mappings"),
                )


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


# @pytest.fixture()
# def es_write_data(es_client, request, event_loop):
#     async def inner(documents: list[dict[str, Any]], index: str):
#         es_actions = get_es_bulk_actions(documents, index)
#         loaded, errors = await async_bulk(client=es_client, actions=es_actions)
#
#         if errors:
#             raise Exception("Ошибка записи данных в Elasticsearch")
#         await es_client.indices.refresh()
#
#     def finalizer():
#         async def clear_es_indices():
#             await es_client.delete_by_query(
#                 index=settings.ES_ALL_INDICES,
#                 query={"match_all": {}},
#             )
#
#         # для выполнения корутины внутри finalizer
#         event_loop.run_until_complete(clear_es_indices())
#
#     request.addfinalizer(finalizer)
#
#     return inner


@pytest.fixture(scope='session')
def es_write_data(es_client):
    async def inner(documents: list[dict[str, Any]], index: str):
        es_actions = get_es_bulk_actions(documents, index)
        loaded, errors = await async_bulk(client=es_client, actions=es_actions)

        if errors:
            raise Exception("Ошибка записи данных в Elasticsearch")

        await es_client.indices.refresh()
        return loaded

    return inner


@pytest.fixture(scope='session')
def es_write_data2(es_client: AsyncElasticsearch):
    async def inner(data: list[dict]):
        return await es_client.bulk(operations=data, refresh=True)

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
