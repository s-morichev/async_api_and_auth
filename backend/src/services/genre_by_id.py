from core.constants import KEY_ID
from elasticsearch import NotFoundError
from models.dto_models import Genre
from models.service_result import ServiceResult
from services.base_service import BaseService


class GenreByIdService(BaseService):
    """Жанр по id"""

    NAME = "GENRE_BY_ID"
    BASE_MODEL = Genre
    IS_LIST_RESULT = False

    async def get_from_elastic(self, query_dict: dict) -> ServiceResult | None:
        index_name = "genres"
        genre_id = query_dict[KEY_ID]
        try:
            resp = await self.elastic.get(index=index_name, id=genre_id)
        except NotFoundError:
            return None

        data_values = {"uuid": resp["_id"]} | resp["_source"]
        result = Genre(**data_values)

        res = self.RESULT_MODEL(total=1, page_num=1, page_size=1, result=result)
        return res
