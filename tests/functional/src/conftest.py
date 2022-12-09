import asyncio
from typing import Any, Iterator

import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from settings import settings
from testdata import genres_schema, movies_schema, persons_schema


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

    await client.indices.delete(index=settings.ES_ALL_INDICES)
    await client.close()


@pytest_asyncio.fixture(scope="session")
async def aiohttp_session():
    session = aiohttp.ClientSession()
    yield session

    await session.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_es_indices(es_client):
    for index, schema in [
        (settings.ES_MOVIES_INDEX, movies_schema),
        (settings.ES_PERSONS_INDEX, persons_schema),
        (settings.ES_GENRES_INDEX, genres_schema),
    ]:
        await es_client.indices.create(
            index=index,
            settings=schema.get("settings"),
            mappings=schema.get("mappings"),
        )


@pytest.fixture()
def es_write_data(es_client, request, event_loop):
    async def inner(documents: list[dict[str, Any]], index: str):
        es_actions = get_es_bulk_actions(documents, index)
        loaded, errors = await async_bulk(client=es_client, actions=es_actions)

        if errors:
            raise Exception("Ошибка записи данных в Elasticsearch")
        await es_client.indices.refresh()

    def finalizer():
        async def clear_es_indices():
            await es_client.delete_by_query(
                index=settings.ES_ALL_INDICES,
                query={"match_all": {}},
            )

        # для выполнения корутины внутри finalizer
        event_loop.run_until_complete(clear_es_indices())

    request.addfinalizer(finalizer)

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
