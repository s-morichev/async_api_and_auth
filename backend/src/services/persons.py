from uuid import UUID

from elasticsearch import NotFoundError

from core.constants import ES_MOVIES_INDEX, ES_PERSONS_INDEX
from models.dto_models import ExtendedFilm, ExtendedPerson
from models.service_result import ServiceListResult, ServiceSingeResult
from services.base_service import BaseService

# ------------------------------------------------------------------------------ #


class FilmsByPersonService(BaseService):
    """Фильмы по персоне"""

    NAME = "FILMS_BY_PERSON"
    RESULT_MODEL = ServiceListResult[ExtendedFilm]

    async def get_from_elastic(
        self, *, page_num: int, page_size: int, person_id: UUID
    ) -> "FilmsByPersonService.RESULT_MODEL | None":
        index_name = ES_MOVIES_INDEX
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
                                "query": {"bool": {"filter": {"term": {"actors.id": str(person_id)}}}},
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"bool": {"filter": {"term": {"directors.id": str(person_id)}}}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"bool": {"filter": {"term": {"writers.id": str(person_id)}}}},
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


# ------------------------------------------------------------------------------ #


class PersonByIdService(BaseService):
    """Персона по id"""

    NAME = "PERSON_BY_ID"
    RESULT_MODEL = ServiceSingeResult[ExtendedPerson]

    async def get_from_elastic(self, *, person_id: UUID) -> "PersonByIdService.RESULT_MODEL | None":
        index_name = ES_PERSONS_INDEX
        try:
            resp = await self.elastic.get(index=index_name, id=str(person_id))
        except NotFoundError:
            return None

        data_values = {"uuid": resp["_id"]} | resp["_source"]
        result = ExtendedPerson(**data_values)

        res = self.RESULT_MODEL(total=1, page_num=1, page_size=1, result=result)
        return res


# ------------------------------------------------------------------------------ #


class PersonSearchService(BaseService):
    """Персона по имени"""

    NAME = "PERSONS_SEARCH"
    RESULT_MODEL = ServiceListResult[ExtendedPerson]

    async def get_from_elastic(
        self, *, page_num: int, page_size: int, query: str
    ) -> "PersonSearchService.RESULT_MODEL | None":
        index_name = ES_PERSONS_INDEX

        es = {
            "from": (page_num - 1) * page_size,
            "size": page_size,
            "query": {"match": {"full_name": {"query": query, "fuzziness": "AUTO"}}},
        }
        try:
            resp = await self.elastic.search(index=index_name, body=es)
        except NotFoundError:
            return None

        total = resp["hits"]["total"]["value"]
        lst_result = []
        for hit in resp["hits"]["hits"]:
            data_values = {"uuid": hit["_id"]} | hit["_source"]
            lst_result += [ExtendedPerson(**data_values)]

        res = self.RESULT_MODEL(total=total, page_num=page_num, page_size=page_size, result=lst_result)
        return res


# ------------------------------------------------------------------------------ #
