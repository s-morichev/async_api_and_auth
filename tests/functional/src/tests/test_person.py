import pytest
import pytest_asyncio

from ..settings import settings
from ..testdata.dto_models import ExtendedFilm, ExtendedPerson
from .common import args, check_multi_response, check_single_response, get_pagination_test_data, ids, load_from_json

pytestmark = pytest.mark.asyncio

# ------------------------------------------------------------------------------ #
total_rows = 20


@pytest_asyncio.fixture(scope="module", autouse=True)
async def prepare_data(es_write_data, flush_data):
    es_index = settings.ES_MOVIES_INDEX
    films = load_from_json("films.json", ExtendedFilm)
    await es_write_data(index=es_index, documents=films, id_key="id", exclude={})

    es_index = settings.ES_PERSONS_INDEX
    persons = load_from_json("persons.json", ExtendedPerson)
    assert total_rows == len(persons)
    await es_write_data(index=es_index, documents=persons, id_key="id", exclude={"id"})


# ------------------------------------------------------------------------------ #
# PERSON_BY_ID, '/api/v1/persons/:UUID
testdata = [
    ({"uuid": "8eee6729-02fd-4180-9593-a6934ae6c4b4"}, {"status": 200, "full_name": "First Person"}, "First test"),
    ({"uuid": "61a4ee5d-5585-4e9b-9130-9805b474c7a4"}, {"status": 200, "full_name": "Person Last"}, "Last test"),
    ({"uuid": "cc462baa-cdef-4b87-94ce-71466ee4fee4"}, {"status": 200, "full_name": "Middle"}, "Middle test"),
    ({"uuid": "88d41c11-8e7a-46f6-9890-205848809f34"}, {"status": 404}, "Not found test"),
    ({"uuid": "invalid uuid is that"}, {"status": 422}, "Invalid uuid"),
]


@pytest.mark.parametrize("query_data, expected_result", argvalues=args(testdata), ids=ids(testdata))
async def test_person_by_id(make_get_request, query_data: dict[str, str | int], expected_result: dict[str, str | int]):
    url = "/api/v1/persons/" + query_data["uuid"]
    body, header, status = await make_get_request(url)

    check_single_response(status, body, expected_result)


# ------------------------------------------------------------------------------ #
# PERSONS_SEARCH, /api/v1/persons/search

testdata = [
    ({"query": "First Person"}, {"status": 200, "full_name": "First Person"}, "First record test"),
    ({"query": "Lucas"}, {"status": 200, "total": 0, "length": 0}, "Not found"),
    ({"query": "Person Last"}, {"status": 200, "full_name": "Person Last"}, "Last record test"),
    ({"query": "First"}, {"status": 200, "full_name": "First Person", "total": 1, "length": 1}, "Exactly one found"),
    ({"query": "Person"}, {"status": 200, "total": total_rows - 1}, "all found, exсlude 1"),
]

# добавляю тест пагинации с параметром 'Person', должен вернуть все записи, кроме Middle
testdata += get_pagination_test_data(total_rows - 1, mixin={"query": "Person"})

# добавляю тест пагинации с пустым списком
testdata += get_pagination_test_data(0, mixin={"query": "Lucas"})


@pytest.mark.parametrize("query_data, expected_result", argvalues=args(testdata), ids=ids(testdata))
async def test_person_search(make_get_request, query_data: dict[str, str | int], expected_result: dict[str, str | int]):
    url = "/api/v1/persons/search"
    body, header, status = await make_get_request(url, query_data)
    check_multi_response(status, body, expected_result)


# ------------------------------------------------------------------------------ #
# PERSON FILMS, /api/v1/persons/:UUID/film

testdata = [
    ({"uuid": "8eee6729-02fd-4180-9593-a6934ae6c4b4"}, {"status": 200, "total": 3}, "First Person films"),
    ({"uuid": "very bad uuid"}, {"status": 422}, "Bad uuid"),
    ({"uuid": "ebce2a35-a423-4fd1-96eb-180740d8c919"}, {"status": 200, "total": 0}, "Not present person"),
    (
        {"uuid": "61a4ee5d-5585-4e9b-9130-9805b474c7a4"},
        {"status": 200, "total": 2, "length": 2, "title": "Movie 3"},
        "Last person",
    ),
    (
        {"uuid": "cc462baa-cdef-4b87-94ce-71466ee4fee4"},
        {"status": 200, "total": 2, "length": 2, "1#title": "Movie 11"},
        "Middle person",
    ),
    (
        {"uuid": "782027dc-861f-4253-9440-17a961711b64"},
        {"status": 200, "total": 6, "length": 6, "0#imdb_rating": 9.5},
        "Person 9",
    ),
]

# добавляюю тест пагинации с параметром uuid  для 'Person 9', 6 фильмов в списке
testdata += get_pagination_test_data(6, mixin={"uuid": "782027dc-861f-4253-9440-17a961711b64"})

# добавляюю тест пагинации с параметром uuid  для пустого списка
testdata += get_pagination_test_data(0, mixin={"uuid": "ebce2a35-a423-4fd1-96eb-180740d8c919"})


@pytest.mark.parametrize("query_data, expected_result", argvalues=args(testdata), ids=ids(testdata))
async def test_persons_film(make_get_request, query_data: dict[str, str | int], expected_result: dict[str, str | int]):
    person_id = query_data["uuid"]
    url = f"/api/v1/persons/{person_id}/film"
    body, header, status = await make_get_request(url, query_data)
    print(body)
    check_multi_response(status, body, expected_result)


async def test_cache(clear_indices, make_get_request):
    """кэш проверять только после тестов! Отдельно нельзя!"""

    url = "/api/v1/persons/" + "cc462baa-cdef-4b87-94ce-71466ee4fee4"
    body, header, status = await make_get_request(url)
    assert status == 200
    assert body["full_name"] == "Middle"

    url = "/api/v1/persons/search"
    query_data = {"query": "Person"}
    body, header, status = await make_get_request(url, query_data)
    assert status == 200
    assert body["total"] == total_rows - 1

    person_id = "cc462baa-cdef-4b87-94ce-71466ee4fee4"
    url = f"/api/v1/persons/{person_id}/film"
    body, header, status = await make_get_request(url, query_data)

    assert status == 200
    assert body["total"] == 2
