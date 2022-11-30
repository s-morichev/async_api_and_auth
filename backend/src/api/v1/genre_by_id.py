from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from core.constants import KEY_ID
from models.api_models import Genre
from services.genre_by_id import GenreByIdService

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.get("/{genre_id}", response_model=Genre)
async def genre_by_id(genre_id: UUID, service: GenreByIdService = Depends(GenreByIdService.get_service)) -> Genre:
    param_dict = {KEY_ID: genre_id}
    answer = await service.get(param_dict)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    # вот здесь то можно и переложить данные
    return answer.result
