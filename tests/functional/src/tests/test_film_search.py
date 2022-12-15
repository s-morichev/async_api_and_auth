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
            genre=["Action", "Drama"],
            genres=[
                Genre(id="14450430-fc1b-4010-830d-f30c944c7175", name="Action"),
                Genre(id="3a9fe666-f161-4612-9b0a-874d2e87f2e3", name="Drama"),
            ],
            title="title consisting of apple carrot",
            description="description carrot cabbage",
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
            genres=[Genre(id="14450430-fc1b-4010-830d-f30c944c7175", name="Action")],
            title="title consisting of cabbage",
            description="description apple carrot",
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
            genre=["Action", "Genre"],
            genres=[
                Genre(id="14450430-fc1b-4010-830d-f30c944c7175", name="Action"),
                Genre(id="61d34c09-08da-44e7-93d2-0c2bb3a9a068", name="Genre"),
            ],
            title="title consisting of apple",
            description="description carrot",
            directors_names=["d1"],
            actors_names=["a1"],
            writers_names=["w1"],
            actors=[Person(id=uuid.uuid4(), name="a1")],
            writers=[Person(id=uuid.uuid4(), name="w1")],
            directors=[Person(id=uuid.uuid4(), name="d1")],
        ),
        ElasticFilm(
            id=uuid.uuid4(),
            imdb_rating=8.5,
            rars_rating=18,
            fw_type="movie",
            genre=["Action", "Drama"],
            genres=[
                Genre(id="14450430-fc1b-4010-830d-f30c944c7175", name="Action"),
                Genre(id="3a9fe666-f161-4612-9b0a-874d2e87f2e3", name="Drama"),
            ],
            title="random",
            description="random",
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
    "search_query, expected_answer",
    [
        ("title", {"status": 200, "total": 3}),
        ("description", {"status": 200, "total": 3}),
        ("genre", {"status": 200, "total": 1}),
        ("non existent", {"status": 200, "total": 0}),
    ],
)
@pytest.mark.asyncio
async def test_basic_search(search_query, expected_answer, make_get_request):
    body, headers, status = await make_get_request("/api/v1/films/search/", query_data={"query": search_query})

    assert status == expected_answer["status"]
    assert body["total"] == expected_answer["total"]


@pytest.mark.parametrize(
    "search_query, expected_answer",
    [
        ("consist", {"status": 200, "total": 3}),
        ("consists", {"status": 200, "total": 3}),
        ("consisted", {"status": 200, "total": 3}),
        ("consisting", {"status": 200, "total": 3}),
    ],
)
@pytest.mark.asyncio
async def test_search_by_word_forms(search_query, expected_answer, make_get_request):
    body, headers, status = await make_get_request("/api/v1/films/search/", query_data={"query": search_query})

    assert status == expected_answer["status"]
    assert body["total"] == expected_answer["total"]


@pytest.mark.asyncio
async def test_search_without_parameters(make_get_request):
    body, headers, status = await make_get_request("/api/v1/films/search/")

    assert status == 200
    assert body["total"] == 0


@pytest.mark.asyncio
async def test_search_is_case_indifferent(make_get_request):
    body, headers, status = await make_get_request("/api/v1/films/search/", query_data={"query": "TiTLe"})

    assert status == 200
    assert body["total"] == 3


@pytest.mark.parametrize(
    "search_query, expected_answer",
    [
        ("dsecription", {"status": 200, "total": 3}),
        ("escription", {"status": 200, "total": 3}),
        ("ffdescription", {"status": 200, "total": 3}),
        ("fffdescription", {"status": 200, "total": 0}),
    ],
)
@pytest.mark.asyncio
async def test_fuzzy_search(search_query, expected_answer, make_get_request):
    body, headers, status = await make_get_request("/api/v1/films/search/", query_data={"query": search_query})

    assert status == expected_answer["status"]
    assert body["total"] == expected_answer["total"]


@pytest.mark.parametrize(
    "search_params, expected_answer",
    [
        ({"query": "title", "filter[genre]": "3a9fe666-f161-4612-9b0a-874d2e87f2e3"}, {"status": 200, "total": 1}),
        ({"query": "title", "filter[genre]": "a48f8db2-7ae2-4bea-8f55-be6590c5b8d4"}, {"status": 200, "total": 0}),
        ({"query": "title", "filter[genre]": "not uuid"}, {"status": 422}),
    ],
)
@pytest.mark.asyncio
async def test_search_by_genre(search_params, expected_answer, make_get_request):
    body, headers, status = await make_get_request("/api/v1/films/search/", query_data=search_params)

    assert status == expected_answer["status"]
    if "total" in body:
        assert body["total"] == expected_answer["total"]


@pytest.mark.parametrize(
    "search_query, expected_answer",
    [
        (
            "apple",
            {
                "status": 200,
                "order": [
                    "edde24a9-65eb-45f4-ac57-e22dfbe4dc2c",
                    "40285ba8-ca04-4112-ae18-050659a838d6",
                    "d35093b8-dd2d-434a-8848-e8765da10a15",
                ],
            },
        ),
        (
            "apple carrot",
            {
                "status": 200,
                "order": [
                    "40285ba8-ca04-4112-ae18-050659a838d6",
                    "d35093b8-dd2d-434a-8848-e8765da10a15",
                    "edde24a9-65eb-45f4-ac57-e22dfbe4dc2c",
                ],
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_order_of_search_results(search_query, expected_answer, make_get_request):
    body, headers, status = await make_get_request("/api/v1/films/search/", query_data={"query": search_query})

    assert status == expected_answer["status"]
    for i, film_id in enumerate(expected_answer["order"]):
        assert body["result"][i]["uuid"] == film_id
