import enum
from http import HTTPStatus
from uuid import UUID

from api.v1.schemas import ExtendedImdbFilm, ImdbFilm, ManyResponse
from core.service_logger import get_logger
from fastapi import APIRouter, Depends, HTTPException, Query
from services.films import FilmByIdService, PopularFilmsService, SearchFilmsService, SimilarFilmsService

logger = get_logger(__name__)

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


@router.get("/", response_model=ManyResponse[ImdbFilm])
async def films_popular(
    sort_by: Sorting = Query(Sorting.imdb_desc, alias="sort"),
    genre_id: UUID | None = Query(None, alias="filter[genre]"),
    page_number: int = Query(DEFAULT_PAGE_NUMBER, alias="page[number]", ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, alias="page[size]", ge=1),
    service: PopularFilmsService = Depends(PopularFilmsService.get_service),
) -> ManyResponse[ImdbFilm]:
    """Получить популярные фильмы (в текущей версии - с наибольшим рейтингом).

    - **sort**: поле для сортировки с префиксом + либо -
    - **filter[genre]**: UUID идентификатор жанра, из которого получить фильмы
    - **page[number]**: номер страницы
    - **page[size]**: количество фильмов на странице
    """
    _validate_pagination(page_number, page_size)
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
    query: str,
    genre_id: UUID | None = Query(None, alias="filter[genre]"),
    page_number: int = Query(DEFAULT_PAGE_NUMBER, alias="page[number]", ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, alias="page[size]", ge=1),
    service: SearchFilmsService = Depends(SearchFilmsService.get_service),
) -> ManyResponse[ImdbFilm]:
    """Найти фильмы.

    - **query**: поисковый запрос
    - **filter[genre]**: UUID идентификатор жанра, в котором выполнить поиск
    - **page[number]**: номер страницы
    - **page[size]**: количество фильмов на странице
    """
    _validate_pagination(page_number, page_size)
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
    film_id: str,
    page_number: int = Query(1, alias="page[number]", ge=1),
    page_size: int = Query(3, alias="page[size]", ge=1),
    service: SimilarFilmsService = Depends(SimilarFilmsService.get_service),
) -> ManyResponse[ImdbFilm]:
    """Получить похожие фильмы (в текущей версии - фильмы того же жанра).

    - **film_id**: UUID идентификатор фильма
    - **page[number]**: номер страницы
    - **page[size]**: количество элементов на странице
    """
    _validate_pagination(page_number, page_size)
    answer = await service.get(
        film_id=film_id,
        page_number=page_number,
        page_size=page_size,
    )

    film_list = [ImdbFilm(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in answer.result]
    return ManyResponse[ImdbFilm](total=answer.total, result=film_list)


@router.get("/{film_id}", response_model=ExtendedImdbFilm)
async def film_details(
    film_id: str, service: FilmByIdService = Depends(FilmByIdService.get_service)
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
