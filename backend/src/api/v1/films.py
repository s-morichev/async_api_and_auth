import enum
import logging
from http import HTTPStatus
from typing import List
from uuid import UUID

from api.v1 import dto_models
from fastapi import APIRouter, Depends, HTTPException, Query
from services.films import PopularFilmsService, SearchFilmsService, FilmByIdService, SimilarFilmsService

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 50
DEFAULT_PAGE_NUMBER = 1
ELASTIC_PAGINATION_LIMIT = 10_000

router = APIRouter()


class Sorting(enum.Enum):
    imdb_asc = "+imdb_rating"
    imdb_desc = "-imdb_rating"


def _validate_pagination(page_number: int, page_size: int):
    if page_number * page_size > ELASTIC_PAGINATION_LIMIT:
        resp = f"Requested film window is too large, page[number] * page[size] must be less than or equal to {ELASTIC_PAGINATION_LIMIT}"
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=resp)


@router.get("/", response_model=List[dto_models.Film])
async def films_popular(
    sort_by: Sorting = Query(Sorting.imdb_desc, alias="sort"),
    genre_id: UUID | None = Query(None, alias="filter[genre]"),
    page_number: int = Query(DEFAULT_PAGE_NUMBER, alias="page[number]", ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, alias="page[size]", ge=1),
    service: PopularFilmsService = Depends(PopularFilmsService.get_service),
) -> List[dto_models.Film]:
    """Получить популярные фильмы (в текущей версии - с наибольшим рейтингом).

    - **sort**: поле для сортировки с префиксом + либо -
    - **filter[genre]**: UUID идентификатор жанра, из которого получить фильмы
    - **page[number]**: номер страницы
    - **page[size]**: количество фильмов на странице
    """
    _validate_pagination(page_number, page_size)
    answer = await service.get_from_elastic(
        sort_by=sort_by.value,
        genre_id=genre_id,
        page_number=page_number,
        page_size=page_size,
    )

    dto_list = [dto_models.Film(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in answer.result]
    return dto_list


@router.get("/search/", response_model=List[dto_models.Film])
async def film_search(
    query: str,
    genre_id: UUID | None = Query(None, alias="filter[genre]"),
    page_number: int = Query(DEFAULT_PAGE_NUMBER, alias="page[number]", ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, alias="page[size]", ge=1),
    service: SearchFilmsService = Depends(SearchFilmsService.get_service),
) -> List[dto_models.Film]:
    """Найти фильмы.

    - **query**: поисковый запрос
    - **filter[genre]**: UUID идентификатор жанра, в котором выполнить поиск
    - **page[number]**: номер страницы
    - **page[size]**: количество фильмов на странице
    """
    _validate_pagination(page_number, page_size)
    answer = await service.get_from_elastic(
        search_for=query,
        genre_id=genre_id,
        page_number=page_number,
        page_size=page_size,
    )

    dto_list = [dto_models.Film(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in
                answer.result]
    return dto_list


@router.get("/{film_id}/similar", response_model=List[dto_models.Film])
async def film_similar(
    film_id: str,
    page_number: int = Query(1, alias="page[number]", ge=1),
    page_size: int = Query(3, alias="page[size]", ge=1),
    service: SimilarFilmsService = Depends(SimilarFilmsService.get_service),
) -> List[dto_models.Film]:
    """Получить похожие фильмы (в текущей версии - фильмы того же жанра).

    - **film_id**: UUID идентификатор фильма
    - **page[number]**: номер страницы
    - **page[size]**: количество элементов на странице
    """
    _validate_pagination(page_number, page_size)
    answer = await service.get_from_elastic(
        film_id=film_id,
        page_number=page_number,
        page_size=page_size,
    )

    dto_list = [dto_models.Film(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in
                answer.result]
    return dto_list


@router.get("/{film_id}", response_model=dto_models.ExtendedFilm)
async def film_details(
        film_id: str,
        service: FilmByIdService = Depends(FilmByIdService.get_service)
) -> dto_models.ExtendedFilm:
    """Получить полную информацию о фильме.

    - **film_id**: UUID идентификатор фильма
    """
    answer = await service.get_from_elastic(film_id=film_id)
    film = answer.result

    return dto_models.ExtendedFilm(
        uuid=film.uuid,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )
