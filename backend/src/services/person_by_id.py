from uuid import UUID

from elasticsearch import NotFoundError
from models.dto_models import ExtendedPerson
from models.service_result import ServiceSingeResult
from services.base_service import BaseService


class PersonByIdService(BaseService):
    """Персона по id"""

    NAME = "PERSON_BY_ID"
    BASE_MODEL = ExtendedPerson
    RESULT_MODEL = ServiceSingeResult[ExtendedPerson]

    async def get_from_elastic(self, *, person_id) -> "PersonByIdService.RESULT_MODEL | None":
        index_name = "persons"
        try:
            resp = await self.elastic.get(index=index_name, id=person_id)
        except NotFoundError:
            return None

        data_values = {"uuid": resp["_id"]} | resp["_source"]
        result = ExtendedPerson(**data_values)

        res = self.RESULT_MODEL(total=1, page_num=1, page_size=1, result=result)
        return res
