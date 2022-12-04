from uuid import UUID

from elasticsearch import NotFoundError

from core.constants import ES_GENRES_INDEX
from models.dto_models import Genre
from models.service_result import ServiceListResult, ServiceSingeResult
from services.base_service import BaseService

# ------------------------------------------------------------------------------ #


class GenreByIdService(BaseService):
    """Жанр по id"""

    NAME = "GENRE_BY_ID"
    RESULT_MODEL = ServiceSingeResult[Genre]

    async def get_from_elastic(self, *, genre_id: UUID) -> "GenreByIdService.RESULT_MODEL | None":
        index_name = ES_GENRES_INDEX
        try:
            resp = await self.elastic.get(index=index_name, id=str(genre_id))
        except NotFoundError:
            return None

        data_values = {"uuid": resp["_id"]} | resp["_source"]
        result = Genre(**data_values)

        res = self.RESULT_MODEL(total=1, page_num=1, page_size=1, result=result)
        return res


# ------------------------------------------------------------------------------ #


class GenresAllService(BaseService):
    """список жанров"""

    NAME = "GENRES_ALL"
    RESULT_MODEL = ServiceListResult[Genre]

    async def get_from_elastic(self, *, page_num: int, page_size: int) -> "GenresAllService.RESULT_MODEL | None":
        index_name = ES_GENRES_INDEX

        es = {"from": (page_num - 1) * page_size, "size": page_size, "query": {"match_all": {}}}

        try:
            resp = await self.elastic.search(index=index_name, body=es)
        except NotFoundError:
            return None

        total = resp["hits"]["total"]["value"]
        lst_result = []
        for hit in resp["hits"]["hits"]:
            data_values = {"uuid": hit["_id"]} | hit["_source"]
            lst_result += [Genre(**data_values)]

        res = self.RESULT_MODEL(total=total, page_num=page_num, page_size=page_size, result=lst_result)
        return res
