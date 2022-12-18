import logging
from uuid import UUID

from models.dto_models import Genre
from models.service_result import ServiceListResult, ServiceSingeResult
from services.base_service import BaseService

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------ #


class GenreByIdService(BaseService):
    """Жанр по id"""

    NAME = "GENRE_BY_ID"
    RESULT_MODEL = ServiceSingeResult[Genre]

    async def get_from_database(self, *, genre_id: UUID) -> "GenreByIdService.RESULT_MODEL | None":
        if (result := await self.database_service.genre_by_id(genre_id)) is None:
            return None

        return self.RESULT_MODEL(total=1, page_num=1, page_size=1, result=result)


# ------------------------------------------------------------------------------ #


class GenresAllService(BaseService):
    """список жанров"""

    NAME = "GENRES_ALL"
    RESULT_MODEL = ServiceListResult[Genre]

    async def get_from_database(self, *, page_num: int, page_size: int) -> "GenresAllService.RESULT_MODEL | None":
        total, result = await self.database_service.genres_all(page_size, page_num)
        if total == 0:
            return None
        return self.RESULT_MODEL(total=total, page_num=page_num, page_size=page_size, result=result)
