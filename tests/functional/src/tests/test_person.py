from http import HTTPStatus

import pytest
import pytest_asyncio

from ..settings import settings
from ..utils.dto_models import ExtendedFilm, ExtendedPerson
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
    (
        {"uuid": "d7bb0cd3-7fb0-4c71-bf97-25538c005f66"},
        {"status": HTTPStatus.OK, "full_name": "First Person"},
        "First test",
    ),
    (
        {"uuid": "9d2635af-174c-4e5e-9b62-dc84f40df778"},
        {"status": HTTPStatus.OK, "full_name": "Person Last"},
        "Last test",
    ),
    ({"uuid": "e9a8e7c3-399b-4864-ba58-5129db1677c0"}, {"status": HTTPStatus.OK, "full_name": "Middle"}, "Middle test"),
    ({"uuid": "88d41c11-8e7a-46f6-9890-205848809f34"}, {"status": HTTPStatus.NOT_FOUND}, "Not found test"),
    ({"uuid": "invalid uuid is that"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}, "Invalid uuid"),
]


@pytest.mark.parametrize("query_data, expected_result", argvalues=args(testdata), ids=ids(testdata))
async def test_person_by_id(make_get_request, query_data: dict[str, str | int], expected_result: dict[str, str | int]):
    url = "/api/v1/persons/" + query_data["uuid"]
    body, header, status = await make_get_request(url)

    check_single_response(status, body, expected_result)


# ------------------------------------------------------------------------------ #
# PERSONS_SEARCH, /api/v1/persons/search

testdata = [
    ({"query": "First Person"}, {"status": HTTPStatus.OK, "full_name": "First Person"}, "First record test"),
    ({"query": "Lucas"}, {"status": HTTPStatus.NOT_FOUND}, "Not found"),
    ({"query": "Person Last"}, {"status": HTTPStatus.OK, "full_name": "Person Last"}, "Last record test"),
    (
        {"query": "First"},
        {"status": HTTPStatus.OK, "full_name": "First Person", "total": 1, "length": 1},
        "Exactly one found",
    ),
    ({"query": "Person"}, {"status": HTTPStatus.OK, "total": total_rows - 1}, "all found, exсlude 1"),
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
    ({"uuid": "d7bb0cd3-7fb0-4c71-bf97-25538c005f66"}, {"status": HTTPStatus.OK, "total": 1}, "First Person films"),
    ({"uuid": "very bad uuid"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}, "Bad uuid"),
    ({"uuid": "ebce2a35-a423-4fd1-96eb-180740d8c919"}, {"status": HTTPStatus.NOT_FOUND}, "Not present person"),
    (
        {"uuid": "9d2635af-174c-4e5e-9b62-dc84f40df778"},
        {"status": HTTPStatus.OK, "total": 2, "length": 2, "title": "Movie 5"},
        "Last person",
    ),
    (
        {"uuid": "e9a8e7c3-399b-4864-ba58-5129db1677c0"},
        {"status": HTTPStatus.OK, "total": 1, "length": 1, "0#title": "Movie 5"},
        "Middle person",
    ),
    (
        {"uuid": "6cb72cd8-eef7-4abc-b4c9-53a57cc77adc"},
        {"status": HTTPStatus.OK, "total": 4, "length": 4, "0#imdb_rating": 7.7},
        "Person 9",
    ),
]

# добавляюю тест пагинации с параметром uuid  для 'Person 9', 4 фильма в списке
testdata += get_pagination_test_data(4, mixin={"uuid": "6cb72cd8-eef7-4abc-b4c9-53a57cc77adc"})

# добавляюю тест пагинации с параметром uuid  для пустого списка Person 18
testdata += get_pagination_test_data(0, mixin={"uuid": "dd94fd84-320a-4103-b41c-293a6188c7f8"})


@pytest.mark.parametrize("query_data, expected_result", argvalues=args(testdata), ids=ids(testdata))
async def test_persons_film(make_get_request, query_data: dict[str, str | int], expected_result: dict[str, str | int]):
    person_id = query_data["uuid"]
    url = f"/api/v1/persons/{person_id}/film"
    body, header, status = await make_get_request(url, query_data)

    check_multi_response(status, body, expected_result)


async def test_cache(clear_indices, make_get_request):
    """кэш проверять только после тестов! Отдельно нельзя!"""

    url = "/api/v1/persons/" + "e9a8e7c3-399b-4864-ba58-5129db1677c0"
    body, header, status = await make_get_request(url)
    assert status == HTTPStatus.OK
    assert body["full_name"] == "Middle"

    url = "/api/v1/persons/search"
    query_data = {"query": "Person"}
    body, header, status = await make_get_request(url, query_data)
    assert status == HTTPStatus.OK
    assert body["total"] == total_rows - 1

    person_id = "e9a8e7c3-399b-4864-ba58-5129db1677c0"
    url = f"/api/v1/persons/{person_id}/film"
    body, header, status = await make_get_request(url, query_data)
    assert status == HTTPStatus.OK
    assert body["total"] == 1
