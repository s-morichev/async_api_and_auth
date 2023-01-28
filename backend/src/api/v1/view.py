import enum
import logging
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.params import PageParams, QueryPageParams
from api.v1.schemas import ExtendedImdbFilm, ImdbFilm, ManyResponse
from core.constants import KEY_FILTER_GENRE, KEY_SORT
from core.utils import can_view_film
from models.token import AccessTokenPayload
from services.films import FilmByIdService, PopularFilmsService, SearchFilmsService, SimilarFilmsService

logger = logging.getLogger(__name__)

router = APIRouter()


from core.auth_bearer import jwt_bearer


@router.get("/{film_id}", summary="get link to view film")
async def view_link(
    film_id: UUID,
    service: FilmByIdService = Depends(FilmByIdService.get_service),
    token_payload: AccessTokenPayload = Depends(jwt_bearer),
) -> str:
    """Получить ссылку для просмотра фильма.

    - **film_id**: UUID идентификатор фильма
    """
    service_result = await service.get(film_id=film_id)
    if not service_result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"film {film_id} not found")

    if not can_view_film(token_payload.roles, service_result.result.marks):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=f"No permission to view film")

    # тут должна быть генерация ссылки для просмотра фильма
    return "link to view film"
