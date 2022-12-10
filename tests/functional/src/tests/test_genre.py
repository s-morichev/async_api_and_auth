import uuid
import pytest
import pytest_asyncio

from src.testdata.dto_models import Person, Genre, ExtendedFilm
from src.settings import settings

pytestmark = pytest.mark.asyncio
# ------------------------------------------------------------------------------ #
total_rows = 4


@pytest_asyncio.fixture(scope='module', autouse=True)
async def prepare_data(es_write_data2, flush_data):
    def create_data(index_name):
        genre_names = ['Action', 'Sci_fi', 'Drama', 'Quest']
        assert len(genre_names) == total_rows
        genres = [Genre(id=uuid.uuid4(), name=name) for name in genre_names]

        result = []
        for row in genres:
            doc = [{"index": {"_index": index_name, "_id": row.id}}, row.dict(exclude={'id'})]
            result.extend(doc)
        return result

    es_index = settings.ES_GENRES_INDEX
    data = create_data(es_index)

    response = await es_write_data2(data)
    if response['errors']:
        print(response)
        raise Exception('Ошибка записи данных в Elasticsearch')


testdata = [
    ({'page[number]': 1, 'page[size]': 50}, {'status': 200, 'total': total_rows}, 'default'),
    ({'page[number]': 1, 'page[size]': 3}, {'status': 200, 'length': 3}, 'limit page=3'),
    ({'page[number]': 1, 'page[size]': 1}, {'status': 200, 'length': 1}, 'limit page=1'),
    ({'page[number]': 2, 'page[size]': 2}, {'status': 200, 'length': 2}, 'limit page=1, page size=2'),
    ({'page[size]': 3}, {'status': 200, 'length': 3}, 'only page size=3'),
    ({'page[number]': 1}, {'status': 200, 'length': total_rows}, 'only page number=1'),
    ({'page[number]': 2}, {'status': 200, 'length': 0}, 'page number=2'),
    ({}, {'status': 200, 'length': total_rows}, 'no pages'),
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
@pytest.mark.asyncio
async def test_list(make_get_request, query_data, expected_result: dict[str, str | int]):
    # шлем запрос
    url = '/api/v1/genres/'
    body, header, status = await make_get_request(url, query_data)

    # проверяем ответ
    if 'status' in expected_result:
        assert status == expected_result['status']

    if 'total' in expected_result:
        assert body['total'] == expected_result['total']

    if 'length' in expected_result:
        assert len(body['result']) == expected_result['length']
