import uuid

import pytest
import pytest_asyncio
from ..settings import settings
from ..testdata.dto_models import ElasticFilm, Genre, Person


@pytest_asyncio.fixture(scope='module', autouse=True)
async def prepare_data(es_write_data, flush_data):
    def create_data(index_name):
        films = [
            ElasticFilm(
                id="47285b2f-499f-421e-9762-015a9d1cdc0d",
                imdb_rating=8.5,
                rars_rating=18,
                fw_type="movie",
                genre=["Action", "Sci-Fi"],
                genres=[Genre(id=uuid.uuid4(), name="genre1"), Genre(id=uuid.uuid4(), name="genre2")],
                title="The Star",
                description="New World",
                directors_names=["Stan"],
                actors_names=["Ann", "Bob"],
                writers_names=["Ben", "Howard"],
                actors=[Person(id=uuid.uuid4(), name="Ann"), Person(id=uuid.uuid4(), name="Bob")],
                writers=[Person(id=uuid.uuid4(), name="Ben"), Person(id=uuid.uuid4(), name="Howard")],
                directors=[Person(id=uuid.uuid4(), name="Dir1"), Person(id=uuid.uuid4(), name="Dir2")],
            )
        ]
        films.extend([
            ElasticFilm(
                id=uuid.uuid4(),
                imdb_rating=8.5,
                rars_rating=18,
                fw_type="movie",
                genre=["Action", "Sci-Fi"],
                genres=[Genre(id=uuid.uuid4(), name="genre1"), Genre(id=uuid.uuid4(), name="genre2")],
                title="The Star",
                description="New World",
                directors_names=["Stan"],
                actors_names=["Ann", "Bob"],
                writers_names=["Ben", "Howard"],
                actors=[Person(id=uuid.uuid4(), name="Ann"), Person(id=uuid.uuid4(), name="Bob")],
                writers=[Person(id=uuid.uuid4(), name="Ben"), Person(id=uuid.uuid4(), name="Howard")],
                directors=[Person(id=uuid.uuid4(), name="Dir1"), Person(id=uuid.uuid4(), name="Dir2")],
            )
            for _ in range(2)
        ])
        return films
        # result = []
        # for row in films:
        #     #doc = [{"index": {"_index": index_name, "_id": row.id}}, row.dict(exclude={'id'})]
        #     doc = [{"index": {"_index": index_name, "_id": row.id}}, row.dict()]
        #     result.extend(doc)
        # return result

    es_index = settings.ES_MOVIES_INDEX
    data = create_data(es_index)

    response = await es_write_data(index=es_index, documents=data, id_key='id', exclude={})


@pytest.mark.parametrize(
    "film_id, expected_answer",
    [
        ("47285b2f-499f-421e-9762-015a9d1cdc0d", {"status": 200, "uuid": "47285b2f-499f-421e-9762-015a9d1cdc0d"}),
        ("e297df8b-1499-4e22-808f-032c78e3054b", {"status": 404}),
        ("not uuid", {"status": 422}),
    ],
)
@pytest.mark.asyncio
async def test_get_film_by_id(film_id, expected_answer, make_get_request):
    body, headers, status = await make_get_request(f"/api/v1/films/{film_id}/")

    assert status == expected_answer["status"]
    if "uuid" in expected_answer:
        assert body["uuid"] == expected_answer["uuid"]


@pytest.mark.parametrize(
    "search_params, expected_answer",
    [
        ({"query": "Star", "page[size]": 2}, {"status": 200, "length": 2}),
        ({"query": "Mashed potato", "page[size]": 3}, {"status": 200, "length": 0}),
    ],
)
@pytest.mark.asyncio
async def test_search(search_params, expected_answer, es_write_data, make_get_request):
    body, headers, status = await make_get_request("/api/v1/films/search/", query_data=search_params)

    assert status == expected_answer["status"]
    assert len(body["result"]) == expected_answer["length"]
