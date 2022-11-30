from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from core.constants import KEY_PAGE_NUM, KEY_PAGE_SIZE
from models.service_result import ServiceResult
from services.genres_all import GenreServie

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.get("/", response_model=GenreServie.RESPONSE_MODEL)
async def genres_list(
    page_size: int | None = Query(default=50, alias=KEY_PAGE_SIZE, title="count of results rows", ge=1),
    page_number: int | None = Query(default=1, alias=KEY_PAGE_NUM, title="number of page (pagination)", ge=1),
    service: GenreServie = Depends(GenreServie.get_service),
) -> ServiceResult:

    param_dict = {KEY_PAGE_NUM: page_number, KEY_PAGE_SIZE: page_size}
    answer = await service.get(param_dict)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="persons not found")

    # вот здесь то можно и переложить данные
    return answer
