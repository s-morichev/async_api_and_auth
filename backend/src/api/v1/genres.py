from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api.v1.params import PageParams
from api.v1.schemas import Genre, ManyResponse
from services.genres import GenreByIdService, GenresAllService

router = APIRouter()


@router.get("/{genre_id}", response_model=Genre, summary="get one genre by id=:genre_id")
async def genre_by_id(genre_id: UUID, service: GenreByIdService = Depends(GenreByIdService.get_service)) -> Genre:
    """Поиск жанра по id"""

    answer = await service.get(genre_id=genre_id)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"genre id:{genre_id} not found")

    result = Genre(**answer.result.dict())
    return result


@router.get("/", response_model=ManyResponse[Genre], summary="get many(all) genres")
async def all_genres(
    params: PageParams = Depends(),
    service: GenresAllService = Depends(GenresAllService.get_service),
) -> ManyResponse[Genre]:
    """
    Список жанров
    - **page[number]**: номер страницы
    - **page[size]**: количество жанров на странице
    """

    params.check_pagination()

    answer = await service.get(page_num=params.page_number, page_size=params.page_size)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genres not found")

    lst_genres = [Genre(**dto.dict()) for dto in answer.result]
    result = ManyResponse[Genre](total=answer.total, result=lst_genres)
    return result
