import uuid

import pytest
import pytest_asyncio

from ..settings import settings
from ..testdata.dto_models import ElasticFilm, Genre, Person


@pytest_asyncio.fixture(scope="module", autouse=True)
async def prepare_data(es_write_data):

    films = [
        ElasticFilm(
            id="40285ba8-ca04-4112-ae18-050659a838d6",
            imdb_rating=8.5,
            rars_rating=18,
            fw_type="movie",
            genre=["Thriller", "Drama"],
            genres=[
                Genre(id="14450430-fc1b-4010-830d-f30c944c7175", name="Thriller"),
                Genre(id="3a9fe666-f161-4612-9b0a-874d2e87f2e3", name="Drama"),
            ],
            title="t1",
            description="d1",
            directors_names=["d1"],
            actors_names=["a1"],
            writers_names=["w1"],
            actors=[Person(id=uuid.uuid4(), name="a1")],
            writers=[Person(id=uuid.uuid4(), name="w1")],
            directors=[Person(id=uuid.uuid4(), name="d1")],
        ),
        ElasticFilm(
            id="d35093b8-dd2d-434a-8848-e8765da10a15",
            imdb_rating=8.5,
            rars_rating=18,
            fw_type="movie",
            genre=["Action"],
            genres=[Genre(id="61d34c09-08da-44e7-93d2-0c2bb3a9a068", name="Action")],
            title="t1",
            description="d1",
            directors_names=["d1"],
            actors_names=["a1"],
            writers_names=["w1"],
            actors=[Person(id=uuid.uuid4(), name="a1")],
            writers=[Person(id=uuid.uuid4(), name="w1")],
            directors=[Person(id=uuid.uuid4(), name="d1")],
        ),
        ElasticFilm(
            id="edde24a9-65eb-45f4-ac57-e22dfbe4dc2c",
            imdb_rating=8.5,
            rars_rating=18,
            fw_type="movie",
            genre=["Action", "Thriller"],
            genres=[
                Genre(id="61d34c09-08da-44e7-93d2-0c2bb3a9a068", name="Action"),
                Genre(id="14450430-fc1b-4010-830d-f30c944c7175", name="Thriller"),
            ],
            title="t1",
            description="d1",
            directors_names=["d1"],
            actors_names=["a1"],
            writers_names=["w1"],
            actors=[Person(id=uuid.uuid4(), name="a1")],
            writers=[Person(id=uuid.uuid4(), name="w1")],
            directors=[Person(id=uuid.uuid4(), name="d1")],
        ),
    ]

    await es_write_data(index=settings.ES_MOVIES_INDEX, documents=films, id_key="id", exclude={})


@pytest.mark.parametrize(
    "film_id, expected_answer",
    [
        ("40285ba8-ca04-4112-ae18-050659a838d6", {"status": 200, "total": 2}),
        ("e297df8b-1499-4e22-808f-032c78e3054b", {"status": 404}),
        ("not uuid", {"status": 422}),
    ],
)
@pytest.mark.asyncio
async def test_get_similar_films(film_id, expected_answer, make_get_request):
    body, headers, status = await make_get_request(f"/api/v1/films/{film_id}/similar")

    assert status == expected_answer["status"]
    if "total" in expected_answer:
        assert body["total"] == expected_answer["total"]
