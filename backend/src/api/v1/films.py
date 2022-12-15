import enum
import logging
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.params import PageParams, QueryPageParams
from api.v1.schemas import ExtendedImdbFilm, ImdbFilm, ManyResponse
from core.constants import KEY_FILTER_GENRE, KEY_SORT
from services.films import FilmByIdService, PopularFilmsService, SearchFilmsService, SimilarFilmsService

logger = logging.getLogger(__name__)

router = APIRouter()


class Sorting(enum.Enum):
    imdb_asc = "+imdb_rating"
    imdb_desc = "-imdb_rating"


@router.get("/", response_model=ManyResponse[ImdbFilm], summary="get many films sorted by :sort")
async def films_popular(
    sort_by: Sorting = Query(Sorting.imdb_desc, alias=KEY_SORT),
    genre_id: UUID | None = Query(None, alias=KEY_FILTER_GENRE),
    params: PageParams = Depends(),
    service: PopularFilmsService = Depends(PopularFilmsService.get_service),
) -> ManyResponse[ImdbFilm]:
    """Получить популярные фильмы (в текущей версии - с наибольшим рейтингом).

    - **sort**: поле для сортировки с префиксом + либо -
    - **filter[genre]**: UUID идентификатор жанра, из которого получить фильмы
    - **page[number]**: номер страницы
    - **page[size]**: количество фильмов на странице
    """

    params.check_pagination()

    answer = await service.get(
        sort_by=sort_by.value,
        genre_id=genre_id,
        page_number=params.page_number,
        page_size=params.page_size,
    )
    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    film_list = [ImdbFilm(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in answer.result]
    return ManyResponse[ImdbFilm](total=answer.total, result=film_list)


@router.get(
    "/search/", response_model=ManyResponse[ImdbFilm], summary="get many films like :query_string and Genre=:genre_id"
)
async def film_search(
    genre_id: UUID | None = Query(None, alias=KEY_FILTER_GENRE),
    params: QueryPageParams = Depends(),
    service: SearchFilmsService = Depends(SearchFilmsService.get_service),
) -> ManyResponse[ImdbFilm]:
    """Найти фильмы.

    - **query**: поисковый запрос
    - **filter[genre]**: UUID идентификатор жанра, в котором выполнить поиск
    - **page[number]**: номер страницы
    - **page[size]**: количество фильмов на странице
    """

    params.check_pagination()

    answer = await service.get(
        search_for=params.query,
        genre_id=genre_id,
        page_number=params.page_number,
        page_size=params.page_size,
    )

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"films like '{params.query}' not found")

    film_list = [ImdbFilm(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in answer.result]
    return ManyResponse[ImdbFilm](total=answer.total, result=film_list)


@router.get("/{film_id}/similar", response_model=ManyResponse[ImdbFilm], summary="get many films similar :film_id")
async def film_similar(
    film_id: UUID,
    params: PageParams = Depends(),
    service: SimilarFilmsService = Depends(SimilarFilmsService.get_service),
) -> ManyResponse[ImdbFilm]:
    """Получить похожие фильмы (в текущей версии - фильмы того же жанра).

    - **film_id**: UUID идентификатор фильма
    - **page[number]**: номер страницы
    - **page[size]**: количество элементов на странице
    """

    params.check_pagination()

    answer = await service.get(
        film_id=film_id,
        page_number=params.page_number,
        page_size=params.page_size,
    )

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"films similar {film_id} not found")

    film_list = [ImdbFilm(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in answer.result]
    return ManyResponse[ImdbFilm](total=answer.total, result=film_list)


@router.get("/{film_id}", response_model=ExtendedImdbFilm, summary="get one film with id=:film_id")
async def film_details(
    film_id: UUID, service: FilmByIdService = Depends(FilmByIdService.get_service)
) -> ExtendedImdbFilm:
    """Получить полную информацию о фильме.

    - **film_id**: UUID идентификатор фильма
    """

    answer = await service.get(film_id=film_id)
    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"film {film_id} not found")

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
