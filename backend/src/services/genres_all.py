from elasticsearch import NotFoundError

from core.constants import KEY_PAGE_NUM, KEY_PAGE_SIZE
from models.api_models import Genre
from models.service_result import ServiceResult
from services.base_service import BaseService


class GenreServie(BaseService):
    """список жанров"""

    NAME = "GENRES_ALL"
    BASE_MODEL = Genre
    IS_LIST_RESULT = True

    async def get_from_elastic(self, query_dict: dict = None) -> ServiceResult | None:

        page_num = query_dict[KEY_PAGE_NUM]
        page_size = query_dict[KEY_PAGE_SIZE]

        index_name = "genres"

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
