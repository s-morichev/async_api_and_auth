from http import HTTPStatus
from uuid import UUID

from core.constants import KEY_ID
from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.schemas import Genre, ManyGenre
from services.genre_by_id import GenreByIdService
from services.genres_all import GenreService
from core.constants import KEY_PAGE_NUM, KEY_PAGE_SIZE

router = APIRouter()


@router.get("/{genre_id}", response_model=Genre, tags=["Жанр по id"])
async def genre_by_id(genre_id: UUID, service: GenreByIdService = Depends(GenreByIdService.get_service)) -> Genre:
    param_dict = {KEY_ID: genre_id}
    answer = await service.get(param_dict)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"genre id:{genre_id} not found")

    result = Genre(**answer.result.dict())
    return result


@router.get("/", response_model=ManyGenre, tags=["Все жанры"])
async def all_genres(
        page_size: int | None = Query(default=50, alias=KEY_PAGE_SIZE, title="count of results rows", ge=1),
        page_number: int | None = Query(default=1, alias=KEY_PAGE_NUM, title="number of page (pagination)", ge=1),
        service: GenreService = Depends(GenreService.get_service),
) -> ManyGenre:

    param_dict = {KEY_PAGE_NUM: page_number, KEY_PAGE_SIZE: page_size}
    answer = await service.get(param_dict)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genres not found")

    lst_genres = [Genre(**dto.dict()) for dto in answer.result]
    result = ManyGenre(total=answer.total, result=lst_genres)
    return result
