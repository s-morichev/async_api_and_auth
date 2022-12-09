import aioredis
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from aioredis import from_url, Redis
import aiohttp
import asyncio
from .settings import settings
import json
from pathlib import Path


# import inspect
#
# def pytest_collection_modifyitems(config, items):
#     for item in items:
#         if inspect.iscoroutinefunction(item.function):
#             item.add_marker(pytest.mark.asyncio)
# ------------------------------------------------------------------------------ #

@pytest.fixture(scope="session")
def event_loop():
    """fixture for session with event_loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
# ------------------------------------------------------------------------------ #


@pytest_asyncio.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=settings.ELK_DSN)
    yield client
    await client.close()
# ------------------------------------------------------------------------------ #


@pytest_asyncio.fixture(scope='session')
async def redis_client() -> aioredis.Redis:
    client = from_url(settings.REDIS_DSN)
    yield client
    await client.close()
# ------------------------------------------------------------------------------ #


@pytest_asyncio.fixture(scope='session')
async def create_indexes(es_client: AsyncElasticsearch, flush_data):
    print('create_indexes')
    path = Path(__file__).parent / 'testdata/'
    #path = Path('../testdata/')
    schemas = ['genres', 'persons', 'movies']
    for index in schemas:
        with open(path / f'{index}_schema.json', 'r') as json_file:
            print(f'create index {index}')
            schema_dict = json.loads(json_file.read())
            await es_client.indices.create(index=index, mappings=schema_dict['mappings'],
                                     settings=schema_dict.get("settings"))
# ------------------------------------------------------------------------------ #


@pytest_asyncio.fixture(scope='session')
async def flush_data(es_client: AsyncElasticsearch, redis_client: aioredis.Redis):
    print('flush')
    await redis_client.flushall()

    indices = await es_client.cat.indices(h='index', s='index')
    if indices:
        indices_str = ','.join(indices.split())
        await es_client.indices.delete(index=indices_str)
# ------------------------------------------------------------------------------ #


@pytest_asyncio.fixture(scope='session', autouse=True)
#@pytest.mark.usefixtures('flush_data', 'create_indexes')
async def init_db(create_indexes):
    print('init_db')
    pass
# ------------------------------------------------------------------------------ #


@pytest.fixture(scope='session')
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict]):
        return await es_client.bulk(operations=data, refresh=True)

    return inner
# ------------------------------------------------------------------------------ #


@pytest_asyncio.fixture(scope='session')
async def http_session():
    async with aiohttp.ClientSession() as session:
        yield session
# ------------------------------------------------------------------------------ #


@pytest.fixture
def call_service(http_session: aiohttp.ClientSession):
    async def inner(service_url, params):
        async with http_session.get(settings.SERVICE_URL+service_url, params=params) as response:
            body = await response.json()
            status = response.status
            return status, body

    return inner
# ------------------------------------------------------------------------------ #
