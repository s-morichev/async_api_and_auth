import pytest
import pytest_asyncio

from ..settings import settings
from ..testdata.dto_models import ElasticFilm
from .common import args, check_multi_response, check_single_response, get_pagination_test_data, ids, load_from_json

pytestmark = pytest.mark.asyncio

# ------------------------------------------------------------------------------ #
total_rows = 20


@pytest_asyncio.fixture(scope="module", autouse=True)
async def prepare_data(es_write_data, flush_data):

    films = load_from_json("films.json", ElasticFilm)
    assert len(films) == total_rows
    es_index = settings.ES_MOVIES_INDEX

    await es_write_data(index=es_index, documents=films, id_key="id", exclude={})


testdata = [
    ({}, {"status": 200, "total": 20, "0#title": "First film", "19#title": "Film Last"}, "default parameters"),
    (
        {"sort": "-imdb_rating"},
        {"status": 200, "total": 20, "0#title": "First film", "19#title": "Film Last"},
        "increasing sort order",
    ),
    (
        {"sort": "+imdb_rating"},
        {"status": 200, "total": 20, "0#title": "Film Last", "19#title": "First film"},
        "decreasing sort order",
    ),
    ({"sort": "invalid sort key"}, {"status": 422}, "invalid sort parameter"),
    (
        {"filter[genre]": "715b726d-2239-4984-99d6-89420a6634c0"},
        {"status": 200, "total": 13, "0#title": "First film", "12#title": "Movie 13"},
        "filter by genre",
    ),
    ({"filter[genre]": "a48f8db2-7ae2-4bea-8f55-be6590c5b8d4"}, {"status": 404}, "filter by non existent genre"),
    ({"filter[genre]": "not uuid"}, {"status": 422}, "filter by genre invalid uuid"),
]
testdata += get_pagination_test_data(20)


@pytest.mark.parametrize("query_data, expected_result", argvalues=args(testdata), ids=ids(testdata))
async def test_films_popular(make_get_request, query_data: dict[str, str | int], expected_result: dict[str, str | int]):
    # шлем запрос
    url = "/api/v1/films/"
    body, header, status = await make_get_request(url, query_data)

    # проверяем ответ
    check_multi_response(status, body, expected_result)


testdata = [
    ({}, {"status": 404}, "default parameters"),
    ({"query": "movie"}, {"status": 200, "total": 18}, "search by title"),
    ({"query": "description"}, {"status": 200, "total": 20}, "search by description"),
    ({"query": "genre"}, {"status": 200, "total": 20}, "search by genre"),
    ({"query": "FiRsT"}, {"status": 200, "total": 1}, "search case insensitive"),
    ({"query": "desription"}, {"status": 200, "total": 20}, "fuzzy without letter"),
    ({"query": "dsecription"}, {"status": 200, "total": 20}, "fuzzy replaced letters"),
    ({"query": "desctiption"}, {"status": 200, "total": 20}, "fuzzy invalid letter"),
    ({"query": "descript"}, {"status": 200, "total": 20}, "different word forms"),
    ({"query": "non existent"}, {"status": 404}, "nothing found"),
    (
        {"query": "movie", "filter[genre]": "715b726d-2239-4984-99d6-89420a6634c0"},
        {"status": 200, "total": 12},
        "filter by genre",
    ),
    (
        {"query": "movie", "filter[genre]": "a48f8db2-7ae2-4bea-8f55-be6590c5b8d4"},
        {"status": 404},
        "filter by non existent genre",
    ),
    ({"query": "movie", "filter[genre]": "not uuid"}, {"status": 422}, "filter by genre invalid uuid"),
]
testdata += get_pagination_test_data(18, mixin={"query": "movie"})


@pytest.mark.parametrize("query_data, expected_result", argvalues=args(testdata), ids=ids(testdata))
async def test_films_search(make_get_request, query_data: dict[str, str | int], expected_result: dict[str, str | int]):
    # шлем запрос
    url = "/api/v1/films/search/"
    body, header, status = await make_get_request(url, query_data)
    # проверяем ответ
    check_multi_response(status, body, expected_result)


testdata = [
    ({"uuid": "edbb87fd-bfdb-458d-852d-61d6f3f67551"}, {"status": 200, "title": "First film"}, "get film"),
    ({"uuid": "a48f8db2-7ae2-4bea-8f55-be6590c5b8d4"}, {"status": 404}, "non existent film"),
    ({"uuid": "not uuid"}, {"status": 422}, "invalid film uuid"),
]


@pytest.mark.parametrize("query_data, expected_result", argvalues=args(testdata), ids=ids(testdata))
async def test_films_by_id(make_get_request, query_data: dict[str, str | int], expected_result: dict[str, str | int]):
    url = f"/api/v1/films/{query_data['uuid']}/"
    body, header, status = await make_get_request(url)

    check_single_response(status, body, expected_result)


testdata = [
    ({"uuid": "edbb87fd-bfdb-458d-852d-61d6f3f67551"}, {"status": 200, "total": 9}, "get similar films"),
    ({"uuid": "a48f8db2-7ae2-4bea-8f55-be6590c5b8d4"}, {"status": 404}, "no similar for non existent film"),
    ({"uuid": "not uuid"}, {"status": 422}, "invalid film uuid"),
]
testdata += get_pagination_test_data(9, mixin={"uuid": "edbb87fd-bfdb-458d-852d-61d6f3f67551"})


@pytest.mark.parametrize("query_data, expected_result", argvalues=args(testdata), ids=ids(testdata))
async def test_films_similar(make_get_request, query_data: dict[str, str | int], expected_result: dict[str, str | int]):
    # шлем запрос
    url = f"/api/v1/films/{query_data['uuid']}/similar"
    body, header, status = await make_get_request(url, query_data)

    # проверяем ответ
    check_multi_response(status, body, expected_result)
