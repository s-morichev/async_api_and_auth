from http import HTTPStatus
from uuid import UUID

from api.v1.schemas import Genre, ManyResponse
from core.utils import validate_pagination
from fastapi import APIRouter, Depends, HTTPException
from services.genres import GenreByIdService, GenresAllService
from params import PageParams
router = APIRouter()


@router.get("/{genre_id}", response_model=Genre)
async def genre_by_id(genre_id: UUID, service: GenreByIdService = Depends(GenreByIdService.get_service)) -> Genre:
    """ Поиск жанра по id"""
    answer = await service.get(genre_id=genre_id)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"genre id:{genre_id} not found")

    result = Genre(**answer.result.dict())
    return result


@router.get("/", response_model=ManyResponse[Genre])
async def all_genres(
        params: PageParams= Depends(),
        service: GenresAllService = Depends(GenresAllService.get_service),
) -> ManyResponse[Genre]:
    """
        Список жанров
        - **page[number]**: номер страницы
        - **page[size]**: количество жанров на странице
    """
    if message := validate_pagination(params.page_number, params.page_size):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=message)

    answer = await service.get(page_num=params.page_number, page_size=params.page_size)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genres not found")

    lst_genres = [Genre(**dto.dict()) for dto in answer.result]
    result = ManyResponse[Genre](total=answer.total, result=lst_genres)
    return result
