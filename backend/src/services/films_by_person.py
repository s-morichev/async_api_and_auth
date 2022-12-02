from core.constants import KEY_ID, KEY_PAGE_NUM, KEY_PAGE_SIZE
from elasticsearch import NotFoundError
from models.dto_models import ExtendedFilm
from models.service_result import ServiceListResult
from services.base_service import BaseService


class FilmsByPersonService(BaseService):
    """Фильмы по персоне"""

    NAME = "FILMS_BY_PERSON"
    BASE_MODEL = ExtendedFilm
    RESULT_MODEL = ServiceListResult[ExtendedFilm]

    async def get_from_elastic(self, *, page_num, page_size, person_id) -> "FilmsByPersonService.RESULT_MODEL | None":
        index_name = "movies"
        es = {
            "from": (page_num - 1) * page_size,
            "size": page_size,
            "sort": [{"imdb_rating": {"order": "desc"}}],
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"bool": {"filter": {"term": {"actors.id": person_id}}}},
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"bool": {"filter": {"term": {"directors.id": person_id}}}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"bool": {"filter": {"term": {"writers.id": person_id}}}},
                            }
                        },
                    ]
                }
            },
        }

        try:
            resp = await self.elastic.search(index=index_name, body=es)
        except NotFoundError:
            return None

        total = resp["hits"]["total"]["value"]
        lst_result = []
        for hit in resp["hits"]["hits"]:
            data_values = {"uuid": hit["_id"]} | hit["_source"]
            lst_result += [ExtendedFilm(**data_values)]

        res = self.RESULT_MODEL(total=total, page_num=page_num, page_size=page_size, result=lst_result)
        return res
