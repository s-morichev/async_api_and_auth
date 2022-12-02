import enum
from http import HTTPStatus
from uuid import UUID

from api.v1.schemas import ExtendedImdbFilm, ImdbFilm, ManyResponse
from core.constants import (
    DEFAULT_PAGE_SIZE,
    KEY_FILTER_GENRE,
    KEY_PAGE_NUM,
    KEY_PAGE_SIZE,
    KEY_QUERY,
    KEY_SORT,
    MAX_PAGE_SIZE,
)
from core.service_logger import get_logger
from core.utils import validate_pagination
from fastapi import APIRouter, Depends, HTTPException, Query
from services.films import FilmByIdService, PopularFilmsService, SearchFilmsService, SimilarFilmsService

logger = get_logger(__name__)

router = APIRouter()


class Sorting(enum.Enum):
    imdb_asc = "+imdb_rating"
    imdb_desc = "-imdb_rating"


@router.get("/", response_model=ManyResponse[ImdbFilm])
async def films_popular(
    sort_by: Sorting = Query(Sorting.imdb_desc, alias=KEY_SORT),
    genre_id: UUID | None = Query(None, alias=KEY_FILTER_GENRE),
    page_number: int = Query(1, alias=KEY_PAGE_NUM, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, alias=KEY_PAGE_SIZE, ge=1, lte=MAX_PAGE_SIZE),
    service: PopularFilmsService = Depends(PopularFilmsService.get_service),
) -> ManyResponse[ImdbFilm]:
    """Получить популярные фильмы (в текущей версии - с наибольшим рейтингом).

    - **sort**: поле для сортировки с префиксом + либо -
    - **filter[genre]**: UUID идентификатор жанра, из которого получить фильмы
    - **page[number]**: номер страницы
    - **page[size]**: количество фильмов на странице
    """
    if message := validate_pagination(page_number, page_size):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=message)

    answer = await service.get(
        sort_by=sort_by.value,
        genre_id=genre_id,
        page_number=page_number,
        page_size=page_size,
    )

    film_list = [ImdbFilm(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in answer.result]
    return ManyResponse[ImdbFilm](total=answer.total, result=film_list)


@router.get("/search/", response_model=ManyResponse[ImdbFilm])
async def film_search(
    query: str = Query(alias=KEY_QUERY),
    genre_id: UUID | None = Query(None, alias=KEY_FILTER_GENRE),
    page_number: int = Query(1, alias=KEY_PAGE_NUM, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, alias=KEY_PAGE_SIZE, ge=1, lte=MAX_PAGE_SIZE),
    service: SearchFilmsService = Depends(SearchFilmsService.get_service),
) -> ManyResponse[ImdbFilm]:
    """Найти фильмы.

    - **query**: поисковый запрос
    - **filter[genre]**: UUID идентификатор жанра, в котором выполнить поиск
    - **page[number]**: номер страницы
    - **page[size]**: количество фильмов на странице
    """
    if message := validate_pagination(page_number, page_size):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=message)
    answer = await service.get(
        search_for=query,
        genre_id=genre_id,
        page_number=page_number,
        page_size=page_size,
    )

    film_list = [ImdbFilm(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in answer.result]
    return ManyResponse[ImdbFilm](total=answer.total, result=film_list)


@router.get("/{film_id}/similar", response_model=ManyResponse[ImdbFilm])
async def film_similar(
    film_id: UUID,
    page_number: int = Query(1, alias=KEY_PAGE_NUM, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, alias=KEY_PAGE_SIZE, ge=1, lte=MAX_PAGE_SIZE),
    service: SimilarFilmsService = Depends(SimilarFilmsService.get_service),
) -> ManyResponse[ImdbFilm]:
    """Получить похожие фильмы (в текущей версии - фильмы того же жанра).

    - **film_id**: UUID идентификатор фильма
    - **page[number]**: номер страницы
    - **page[size]**: количество элементов на странице
    """
    if message := validate_pagination(page_number, page_size):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=message)
    answer = await service.get(
        film_id=film_id,
        page_number=page_number,
        page_size=page_size,
    )

    film_list = [ImdbFilm(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in answer.result]
    return ManyResponse[ImdbFilm](total=answer.total, result=film_list)


@router.get("/{film_id}", response_model=ExtendedImdbFilm)
async def film_details(
    film_id: UUID, service: FilmByIdService = Depends(FilmByIdService.get_service)
) -> ExtendedImdbFilm:
    """Получить полную информацию о фильме.

    - **film_id**: UUID идентификатор фильма
    """
    answer = await service.get(film_id=film_id)
    film = answer.result

    return ExtendedImdbFilm(
        uuid=film.uuid,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )
