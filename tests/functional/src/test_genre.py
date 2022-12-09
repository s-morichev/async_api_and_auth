import uuid
import pytest
import pytest_asyncio
from faker import Faker

from elasticsearch import AsyncElasticsearch
from aioredis import Redis

#from tests.functional.settings import settings
from .dto_models import Person, Genre, ExtendedFilm

pytestmark = pytest.mark.asyncio
# ------------------------------------------------------------------------------ #

@pytest_asyncio.fixture(scope='session', autouse=True)
async def prepare_data(es_write_data, init_db):
    def create_data(index_name):
        fake = Faker()

        genre_names = ['Action', 'Sci_fi', 'Drama', 'Quest']
        genres = [Genre(id=uuid.uuid4(), name=name) for name in genre_names]

        result = []
        for row in genres:
            doc = [{"index": {"_index": index_name, "_id": row.id}}, row.dict(exclude={'id'})]
            result.extend(doc)
        return result

    es_index = 'genres'
    data = create_data(es_index)

    response = await es_write_data(data)
    if response['errors']:
        print(response)
        raise Exception('Ошибка записи данных в Elasticsearch')

total = 4
testdata = [
        ({'page[number]': 1, 'page[size]': 50}, {'status': 200, 'total': total}, 'default'),
        ({'page[number]': 1, 'page[size]': 3}, {'status': 200, 'length': 3}, 'limit page=3'),
        ({'page[number]': 1, 'page[size]': 1}, {'status': 200, 'length': 1}, 'limit page=1'),
        ({'page[number]': 2, 'page[size]': 2}, {'status': 200, 'length': 2}, 'limit page=1, page size=2'),
        ({'page[size]': 3}, {'status': 200, 'length': 3}, 'only page size=3'),
        ({'page[number]': 1}, {'status': 200, 'length': total}, 'only page number=1'),
        ({'page[number]': 2}, {'status': 200, 'length': 0}, 'page number=2'),
        ({}, {'status': 200, 'length': total}, 'no pages'),
        ({'page[number]': 500, 'page[size]': 10}, {'status': 200}, 'big page_number=500'),
        ({'page[number]': -1, 'page[size]': 3}, {'status': 422}, 'page_num=-1'),
        ({'page[number]': 0, 'page[size]': 3}, {'status': 422}, 'page_num=0'),
        ({'page[number]': 1000, 'page[size]': 1000}, {'status': 422}, 'big page size and page num'),
        ({'page[number]': 2, 'page[size]': 500}, {'status': 422}, 'big page_size=500')
    ]


def args(data: list[dict | str]):
    return [row[:2] for row in data]


def ids(data: list[dict | str]):
    return [row[2] for row in data]


@pytest.mark.parametrize('query_data, expected_result', argvalues=args(testdata), ids=ids(testdata))
async def test_list(call_service, query_data, expected_result):
    # шлем запрос
    url = '/api/v1/genres/'
    status, body = await call_service(url, query_data)

    # проверяем ответ
    if 'status' in expected_result:
        assert status == expected_result['status']

    if 'total' in expected_result:
        assert body['total'] == expected_result['total']

    if 'length' in expected_result:
        assert len(body['result']) == expected_result['length']
