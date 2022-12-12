import uuid

import pytest
import pytest_asyncio
from ..settings import settings
from ..testdata.dto_models import ElasticFilm, Genre, Person


@pytest_asyncio.fixture(scope='module', autouse=True)
async def prepare_data(es_write_data):
    films = [
        ElasticFilm(
            id="47285b2f-499f-421e-9762-015a9d1cdc0d",
            imdb_rating=10,
            rars_rating=18,
            fw_type="movie",
            genre=["g1"],
            genres=[Genre(id=uuid.uuid4(), name="g1")],
            title="title",
            description="description",
            directors_names=["d1"],
            actors_names=["a1"],
            writers_names=["w1"],
            actors=[Person(id=uuid.uuid4(), name="a1")],
            writers=[Person(id=uuid.uuid4(), name="w1")],
            directors=[Person(id=uuid.uuid4(), name="d1")],
        )
    ]
    await es_write_data(index=settings.ES_MOVIES_INDEX, documents=films, id_key='id', exclude={})


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
