from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from core.constants import KEY_ID
from models.api_models import ExtendedPerson
from services.person_by_id import PersonByIdService

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.get("/{person_id}", response_model=ExtendedPerson)
async def genre_by_id(
    person_id: UUID, service: PersonByIdService = Depends(PersonByIdService.get_service)
) -> ExtendedPerson:

    param_dict = {KEY_ID: person_id}
    answer = await service.get(param_dict)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    # вот здесь то можно и переложить данные
    return answer.result
