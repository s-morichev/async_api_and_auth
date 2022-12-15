import logging
from uuid import UUID

from models import dto_models
from models.service_result import ServiceListResult, ServiceSingeResult
from services.base_service import BaseService

logger = logging.getLogger(__name__)


class PopularFilmsService(BaseService):
    """Популярные фильмы."""

    NAME = "POPULAR_FILMS"
    RESULT_MODEL = ServiceListResult[dto_models.ImdbFilm]

    async def get_from_database(
        self,
        *,
        sort_by: str,
        genre_id: UUID | None,
        page_number: int,
        page_size: int,
    ) -> "PopularFilmsService.RESULT_MODEL | None":
        total, result = await self.database_service.films_all(sort_by, page_size, page_number, genre_id)
        if total == 0:
            return None
        return self.RESULT_MODEL(total=total, page_num=page_number, page_size=page_size, result=result)


class SearchFilmsService(BaseService):
    """Поиск фильмов."""

    NAME = "SEARCH_FILMS"
    RESULT_MODEL = ServiceListResult[dto_models.ImdbFilm]

    async def get_from_database(
        self,
        *,
        search_for: str,
        genre_id: UUID,
        page_number: int,
        page_size: int,
    ) -> "SearchFilmsService.RESULT_MODEL | None":
        total, result = await self.database_service.films_search(search_for, page_size, page_number, genre_id)
        if total == 0:
            return None
        return self.RESULT_MODEL(total=total, page_num=page_number, page_size=page_size, result=result)


class FilmByIdService(BaseService):
    """Фильм по id."""

    NAME = "FILM_BY_ID"
    RESULT_MODEL = ServiceSingeResult[dto_models.ExtendedFilm]

    async def get_from_database(self, *, film_id: UUID) -> "FilmByIdService.RESULT_MODEL | None":
        if (result := await self.database_service.film_by_id(film_id)) is None:
            return None

        return self.RESULT_MODEL(total=1, page_num=1, page_size=1, result=result)


class SimilarFilmsService(BaseService):
    """Похожие фильмы."""

    NAME = "SIMILAR_FILMS"
    RESULT_MODEL = ServiceListResult[dto_models.ImdbFilm]

    async def get_from_database(
        self,
        *,
        film_id: UUID,
        page_number: int,
        page_size: int,
    ) -> "SimilarFilmsService.RESULT_MODEL | None":
        if (film := await self.database_service.film_by_id(film_id)) is None:
            return None
        # у фильма нет жанров :(
        if not film.genres:
            return None

        genre_id = film.genres[0].uuid

        total, result = await self.database_service.films_all("-imdb_rating", page_size, page_number, genre_id)
        if total == 0:
            return None
        return self.RESULT_MODEL(total=total, page_num=page_number, page_size=page_size, result=result)
