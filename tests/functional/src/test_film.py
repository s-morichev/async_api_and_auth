import uuid

import pytest

from settings import settings

es_three_films_the_star = [
    {
        "id": str(uuid.uuid4()),
        "imdb_rating": 8.5,
        "rars_rating": 18,
        "fw_type": "movie",
        "genre": ["Action", "Sci-Fi"],
        "genres": [{"id": str(uuid.uuid4()), "name": "g1"}, {"id": str(uuid.uuid4()), "name": "g2"}],
        "title": "The Star",
        "description": "New World",
        "directors_names": ["Stan"],
        "actors_names": ["Ann", "Bob"],
        "writers_names": ["Ben", "Howard"],
        "actors": [{"id": str(uuid.uuid4()), "name": "Ann"}, {"id": str(uuid.uuid4()), "name": "Bob"}],
        "writers": [{"id": str(uuid.uuid4()), "name": "Ben"}, {"id": str(uuid.uuid4()), "name": "Howard"}],
        "directors": [{"id": str(uuid.uuid4()), "name": "Dir1"}, {"id": str(uuid.uuid4()), "name": "Dir2"}],
    }
    for _ in range(3)
]


@pytest.mark.asyncio
async def test_get_film_by_id(es_write_data, make_get_request):
    await es_write_data(es_three_films_the_star, settings.ES_MOVIES_INDEX)
    film_id = es_three_films_the_star[0]["id"]
    body, headers, status = await make_get_request(f"/api/v1/films/{film_id}/")

    assert status == 200
    assert body["uuid"] == film_id


@pytest.mark.parametrize(
    "search_params, expected_answer",
    [
        ({"query": "Star", "page[size]": 2}, {"status": 200, "length": 2}),
        ({"query": "Mashed potato", "page[size]": 3}, {"status": 200, "length": 0}),
    ],
)
@pytest.mark.asyncio
async def test_search(search_params, expected_answer, es_write_data, make_get_request):
    await es_write_data(es_three_films_the_star, settings.ES_MOVIES_INDEX)
    body, headers, status = await make_get_request("/api/v1/films/search/", query_data=search_params)

    assert status == expected_answer["status"]
    assert len(body["result"]) == expected_answer["length"]
