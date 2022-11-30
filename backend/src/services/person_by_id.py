from elasticsearch import NotFoundError

from core.constants import KEY_ID
from models.api_models import ExtendedPerson
from models.service_result import ServiceResult
from services.base_service import BaseService


class PersonByIdService(BaseService):
    """Персона по id"""

    NAME = "PERSON_BY_ID"
    BASE_MODEL = ExtendedPerson
    IS_LIST_RESULT = False

    async def get_from_elastic(self, query_dict: dict) -> ServiceResult | None:
        index_name = "persons"
        person_id = query_dict[KEY_ID]
        try:
            resp = await self.elastic.get(index=index_name, id=person_id)
        except NotFoundError:
            return None

        data_values = {"uuid": resp["_id"]} | resp["_source"]
        result = ExtendedPerson(**data_values)

        res = self.RESULT_MODEL(total=1, page_num=1, page_size=1, result=result)
        return res