from http import HTTPStatus
from typing import List
import enum
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from services.films import FilmService, get_film_service
from api.v1 import dto_models

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class Sorting(enum.Enum):
    imdb_asc = "+imdb_rating"
    imdb_desc = "-imdb_rating"


class Filtering(enum.Enum):
    genre = "filter[genre]"


@router.get("/", response_model=List[dto_models.Film])
async def films_popular(
    sort_by: Sorting = Query(Sorting.imdb_desc, alias="sort"),
    genre_id: UUID | None = Query(None, alias="filter[genre]"),
    page_number: int = Query(1, alias="page[number]", ge=1),
    page_size: int = Query(50, alias="page[size]", ge=1),
    film_service: FilmService = Depends(get_film_service),
) -> List[dto_models.Film]:
    films = await film_service.search(
        sort_field=sort_by.value,
        filter_genre=genre_id,
        page_number=page_number,
        page_size=page_size
    )
    return [dto_models.Film(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]


@router.get("/search/", response_model=List[dto_models.Film])
async def film_search(
    query: str,
    genre_id: UUID | None = Query(None, alias="filter[genre]"),
    page_number: int = Query(1, alias="page[number]", ge=1),
    page_size: int = Query(50, alias="page[size]", ge=1),
    film_service: FilmService = Depends(get_film_service),
) -> List[dto_models.Film]:
    """Найти фильмы"""
    films = await film_service.search(query, page_number=page_number, page_size=page_size, filter_genre=genre_id)
    return [dto_models.Film(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]


@router.get("/{film_id}/similar", response_model=List[dto_models.Film])
async def film_similar(
    film_id: str,
    page_number: int = Query(1, alias="page[number]", ge=1),
    page_size: int = Query(3, alias="page[size]", ge=1),
    film_service: FilmService = Depends(get_film_service),
) -> List[dto_models.Film]:
    """Найти фильмы"""
    films = await film_service.get_similar_by_id(film_id, page_number=page_number, page_size=page_size)
    return [dto_models.Film(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]


@router.get("/{film_id}", response_model=dto_models.ExtendedFilm)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> dto_models.ExtendedFilm:
    """Получить полную информацию о фильме.

    - **film_id**: идентификатор фильма
    """
    film = await film_service.get_by_id(film_id)
    logger.debug("film in route %s", film)
    if film is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return dto_models.ExtendedFilm(
        uuid=film.uuid,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors
    )
