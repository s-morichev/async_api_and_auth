from http import HTTPStatus
from uuid import UUID

from api.v1.schemas import Genre, ManyResponse
from core.constants import KEY_PAGE_NUM, KEY_PAGE_SIZE
from core.utils import validate_pagination
from fastapi import APIRouter, Depends, HTTPException, Query
from services.genres  import GenreByIdService, GenresAllService

router = APIRouter()


@router.get("/{genre_id}", response_model=Genre)
async def genre_by_id(genre_id: UUID, service: GenreByIdService = Depends(GenreByIdService.get_service)) -> Genre:
    answer = await service.get(genre_id=genre_id)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"genre id:{genre_id} not found")

    result = Genre(**answer.result.dict())
    return result


@router.get("/", response_model=ManyResponse[Genre])
async def all_genres(
    page_size: int = Query(default=50, alias=KEY_PAGE_SIZE, title="count of results rows", ge=1),
    page_number: int = Query(default=1, alias=KEY_PAGE_NUM, title="number of page (pagination)", ge=1),
    service: GenresAllService = Depends(GenresAllService.get_service),
) -> ManyResponse[Genre]:

    if message := validate_pagination(page_number, page_size):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=message)

    answer = await service.get(page_num=page_number, page_size=page_size)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genres not found")

    lst_genres = [Genre(**dto.dict()) for dto in answer.result]
    result = ManyResponse[Genre](total=answer.total, result=lst_genres)
    return result
