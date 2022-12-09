import uuid
import pytest
import pytest_asyncio

from elasticsearch import AsyncElasticsearch
from aioredis import Redis
from faker import Faker
import random
from tests.functional.settings import settings
from .dto_models import Person, Genre, ExtendedFilm

#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий.
# тогда все тесты так пометит
pytestmark = pytest.mark.asyncio


# ------------------------------------------------------------------------------ #

@pytest_asyncio.fixture(scope='session', autouse=True)
#async def prepare_data(es_write_data, init_db):
async def prepare_data(es_write_data):
    def create_data(index_name):
        fake_ru = Faker('ru_RU')
        fake_en = Faker()
        ru_names = [fake_ru.name() for _ in range(20)]
        en_names = [fake_en.name() for _ in range(20)]

        persons = [Person(id=uuid.uuid4(), full_name=name) for name in (ru_names+en_names)]
        genre_names = ['Action', 'Sci_fi']
        genres = [Genre(id=uuid.uuid4(), name=name) for name in genre_names]

        es_data = [ExtendedFilm(id=uuid.uuid4(), title=f'Star wars chapter:{i}',
                                imdb_rating=1,
                                description='auto',
                                fw_type='Movie',
                                rars_rating=6,
                                genres=genres,
                                actors=random.sample(persons, random.randint(0, 4)),
                                writers=random.sample(persons, random.randint(0, 4)),
                                directors=random.sample(persons, random.randint(0, 4))
                                ) for i in range(60)]
        result = []
        for row in es_data:
            doc = [{"index": {"_index": index_name, "_id": row.id}}, row.dict()]
            result.extend(doc)

            # doc = {"_index": index_name, "_id": row.uuid, "_source": row.dict()}
            # result.append(doc)
        return result

    es_index = 'movies'
    data = create_data(es_index)

    response = await es_write_data(data)
    if response['errors']:
        print(response)
        raise Exception('Ошибка записи данных в Elasticsearch')



# ------------------------------------------------------------------------------ #

async def test_connections(es_client: AsyncElasticsearch, redis_client: Redis):
    es_is_ready = await es_client.ping()
    redis_is_ready = await redis_client.ping()

    assert es_is_ready
    assert redis_is_ready

# ------------------------------------------------------------------------------ #

async def test_search(call_service):
    # шлем запрос
    url = '/api/v1/films/search/'
    query_data = {'query': 'Star'}
    status, body = await call_service(url, query_data)

    # проверяем ответ
    assert status == 200
    assert body['total'] == 60
    assert len(body['result']) == 50

# ------------------------------------------------------------------------------ #
