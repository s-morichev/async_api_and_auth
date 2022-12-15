import pytest
import pytest_asyncio

from ..settings import settings
from ..testdata.dto_models import Genre
from .common import args, check_multi_response, check_single_response, get_pagination_test_data, ids, load_from_json

pytestmark = pytest.mark.asyncio

# ------------------------------------------------------------------------------ #
total_rows = 6


@pytest_asyncio.fixture(scope="module", autouse=True)
async def prepare_data(es_write_data, flush_data):

    genres = load_from_json("genres.json", Genre)
    assert len(genres) == total_rows
    es_index = settings.ES_GENRES_INDEX

    await es_write_data(index=es_index, documents=genres, id_key="id", exclude={"id"})


# ------------------------------------------------------------------------------ #
# GENRES ALL, /api/v1/genres, проверка пагинации
testdata = get_pagination_test_data(total_row_count=total_rows, default_page_size=50, max_page_size=200)


@pytest.mark.parametrize("query_data, expected_result", argvalues=args(testdata), ids=ids(testdata))
async def test_list_pagination(
    make_get_request, query_data: dict[str, str | int], expected_result: dict[str, str | int]
):
    # шлем запрос
    url = "/api/v1/genres/"
    body, header, status = await make_get_request(url, query_data)

    # проверяем ответ
    check_multi_response(status, body, expected_result)


# ------------------------------------------------------------------------------ #
# GENRES ALL, /api/v1/genres
testdata = [({"page[number]": 1, "page[size]": 50}, {"status": 200, "total": total_rows}, "simple check")]


@pytest.mark.parametrize("query_data, expected_result", argvalues=args(testdata), ids=ids(testdata))
async def test_list(make_get_request, query_data: dict[str, str | int], expected_result: dict[str, str | int]):
    # шлем запрос
    url = "/api/v1/genres/"
    body, header, status = await make_get_request(url, query_data)

    # проверяем ответ
    check_multi_response(status, body, expected_result)


# ------------------------------------------------------------------------------ #
# GENRE BY ID, /api/v1/genres/:UUID
testdata = [
    ({"uuid": "c44b71d9-5c6f-4367-9993-89e805c44bcd"}, {"status": 200, "name": "First Genre"}, "First test"),
    ({"uuid": "a6121119-76bc-4d65-9693-efcdc9b56056"}, {"status": 200, "name": "Genre Last"}, "Last test"),
    ({"uuid": "ccb8fb65-5d48-4034-96ce-722e1b452e41"}, {"status": 200, "name": "Middle"}, "Middle test"),
    ({"uuid": "88d41c11-8e7a-46f6-9890-205848809f34"}, {"status": 404}, "Not found test"),
    ({"uuid": "invalid uuid is that"}, {"status": 422}, "Invalid uuid"),
]


@pytest.mark.parametrize("query_data, expected_result", argvalues=args(testdata), ids=ids(testdata))
async def test_genre_by_id(make_get_request, query_data: dict[str, str | int], expected_result: dict[str, str | int]):
    url = "/api/v1/genres/" + query_data["uuid"]
    body, header, status = await make_get_request(url)

    check_single_response(status, body, expected_result)


async def test_cache(clear_indices, make_get_request):
    """кэш проверять только после тестов! Отдельно нельзя!"""
    url = "/api/v1/genres/"
    query_data = {"page[number]": 1, "page[size]": 50}
    body, header, status = await make_get_request(url, query_data)
    assert status == 200

    url = "/api/v1/genres/" + "a6121119-76bc-4d65-9693-efcdc9b56056"
    body, header, status = await make_get_request(url)
    assert status == 200
    assert body["name"] == "Genre Last"
