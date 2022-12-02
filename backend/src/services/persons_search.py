from core.constants import KEY_PAGE_NUM, KEY_PAGE_SIZE, KEY_QUERY
from elasticsearch import NotFoundError
from models.dto_models import ExtendedPerson
from models.service_result import ServiceListResult
from services.base_service import BaseService


class PersonSearchService(BaseService):
    """Персона по имени"""

    NAME = "PERSONS_SEARCH"
    BASE_MODEL = ExtendedPerson
    RESULT_MODEL = ServiceListResult[ExtendedPerson]

    async def get_from_elastic(self, *, page_num, page_size, query) -> "PersonSearchService.RESULT_MODEL | None":
        index_name = "persons"

        es = {
            "from": (page_num - 1) * page_size,
            "size": page_size,
            "query": {"match": {"full_name": {"query": query}}},
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
