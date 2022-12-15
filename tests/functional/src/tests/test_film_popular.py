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
            imdb_rating=9.0,
            rars_rating=18,
            fw_type="movie",
            genre=["Action", "Drama"],
            genres=[
                Genre(id="14450430-fc1b-4010-830d-f30c944c7175", name="Action"),
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
            imdb_rating=8.0,
            rars_rating=18,
            fw_type="movie",
            genre=["Action"],
            genres=[Genre(id="14450430-fc1b-4010-830d-f30c944c7175", name="Action")],
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
            imdb_rating=7.0,
            rars_rating=18,
            fw_type="movie",
            genre=["Action", "Drama"],
            genres=[
                Genre(id="14450430-fc1b-4010-830d-f30c944c7175", name="Action"),
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
    ]

    await es_write_data(index=settings.ES_MOVIES_INDEX, documents=films, id_key="id", exclude={})


@pytest.mark.asyncio
async def test_default_order_of_popular_results(
    make_get_request,
):
    body, headers, status = await make_get_request("/api/v1/films/")

    assert status == 200
    order = [
        "40285ba8-ca04-4112-ae18-050659a838d6",
        "d35093b8-dd2d-434a-8848-e8765da10a15",
        "edde24a9-65eb-45f4-ac57-e22dfbe4dc2c",
    ]
    for i, film_id in enumerate(order):
        assert body["result"][i]["uuid"] == film_id


@pytest.mark.parametrize(
    "query_params, expected_answer",
    [
        (
            {"sort": "-imdb_rating"},
            {
                "status": 200,
                "order": [
                    "40285ba8-ca04-4112-ae18-050659a838d6",
                    "d35093b8-dd2d-434a-8848-e8765da10a15",
                    "edde24a9-65eb-45f4-ac57-e22dfbe4dc2c",
                ],
            },
        ),
        (
            {"sort": "+imdb_rating"},
            {
                "status": 200,
                "order": [
                    "edde24a9-65eb-45f4-ac57-e22dfbe4dc2c",
                    "d35093b8-dd2d-434a-8848-e8765da10a15",
                    "40285ba8-ca04-4112-ae18-050659a838d6",
                ],
            },
        ),
        ({"sort": "invalid_sorting"}, {"status": 422}),
    ],
)
@pytest.mark.asyncio
async def test_order_of_popular_results(query_params, expected_answer, make_get_request):
    body, headers, status = await make_get_request("/api/v1/films/", query_data=query_params)

    assert status == expected_answer["status"]
    if "result" in expected_answer:
        for i, film_id in enumerate(expected_answer["order"]):
            assert body["result"][i]["uuid"] == film_id


@pytest.mark.parametrize(
    "query_params, expected_answer",
    [
        (
            {"filter[genre]": "3a9fe666-f161-4612-9b0a-874d2e87f2e3"},
            {"status": 200, "order": ["40285ba8-ca04-4112-ae18-050659a838d6", "edde24a9-65eb-45f4-ac57-e22dfbe4dc2c"]},
        ),
        ({"filter[genre]": "a48f8db2-7ae2-4bea-8f55-be6590c5b8d4"}, {"status": 200, "order": []}),
        ({"filter[genre]": "not uuid"}, {"status": 422}),
    ],
)
@pytest.mark.asyncio
async def test_filter_popular_by_genre(query_params, expected_answer, make_get_request):
    body, headers, status = await make_get_request("/api/v1/films/", query_data=query_params)

    assert status == expected_answer["status"]
    if "result" in body:
        for i, film_id in enumerate(expected_answer["order"]):
            assert body["result"][i]["uuid"] == film_id
