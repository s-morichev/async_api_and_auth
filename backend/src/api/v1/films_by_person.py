from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from core.constants import KEY_ID, KEY_PAGE_NUM, KEY_PAGE_SIZE
from models.service_result import ServiceResult
from services.films_by_person import FilmsByPersonService

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.get("/{person_id}/film", response_model=FilmsByPersonService.RESPONSE_MODEL)
async def films_by_person(
    person_id: UUID,
    page_size: int | None = Query(default=50, alias=KEY_PAGE_SIZE, title="count of results rows", ge=1),
    page_number: int | None = Query(default=1, alias=KEY_PAGE_NUM, title="number of page (pagination)", ge=1),
    service: FilmsByPersonService = Depends(FilmsByPersonService.get_service),
) -> ServiceResult:

    param_dict = {KEY_PAGE_NUM: page_number, KEY_PAGE_SIZE: page_size, KEY_ID: person_id}

    answer = await service.get(param_dict)
    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    # вот здесь то можно и переложить данные
    return answer
