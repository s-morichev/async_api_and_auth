from uuid import UUID

from models.dto_models import ExtendedPerson, ImdbFilm
from models.service_result import ServiceListResult, ServiceSingeResult
from services.base_service import BaseService

# ------------------------------------------------------------------------------ #


class FilmsByPersonService(BaseService):
    """Фильмы по персоне"""

    NAME = "FILMS_BY_PERSON"
    RESULT_MODEL = ServiceListResult[ImdbFilm]

    async def get_from_database(
        self, *, page_num: int, page_size: int, person_id: UUID
    ) -> "FilmsByPersonService.RESULT_MODEL | None":
        total, result = await self.database_service.person_films(person_id, page_size, page_num)
        if total == 0:
            return None
        return self.RESULT_MODEL(total=total, page_num=page_num, page_size=page_size, result=result)


# ------------------------------------------------------------------------------ #


class PersonByIdService(BaseService):
    """Персона по id"""

    NAME = "PERSON_BY_ID"
    RESULT_MODEL = ServiceSingeResult[ExtendedPerson]

    async def get_from_database(self, *, person_id: UUID) -> "PersonByIdService.RESULT_MODEL | None":
        if (result := await self.database_service.person_by_id(person_id)) is None:
            return None

        return self.RESULT_MODEL(total=1, page_num=1, page_size=1, result=result)


# ------------------------------------------------------------------------------ #


class PersonSearchService(BaseService):
    """Персона по имени"""

    NAME = "PERSONS_SEARCH"
    RESULT_MODEL = ServiceListResult[ExtendedPerson]

    async def get_from_database(
        self, *, page_num: int, page_size: int, query: str
    ) -> "PersonSearchService.RESULT_MODEL | None":
        total, result = await self.database_service.persons_search(query, page_size, page_num)
        if total == 0:
            return None
        return self.RESULT_MODEL(total=total, page_num=page_num, page_size=page_size, result=result)


# ------------------------------------------------------------------------------ #
