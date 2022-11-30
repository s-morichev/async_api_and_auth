from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from core.constants import KEY_PAGE_NUM, KEY_PAGE_SIZE, KEY_QUERY
from models.service_result import ServiceResult
from services.persons_search import PersonSearchService

router = APIRouter()


@router.get("/", response_model=PersonSearchService.RESPONSE_MODEL)
async def person_search(
    query: str | None = Query(default="", alias=KEY_QUERY, title="string for search"),
    page_size: int | None = Query(default=50, alias=KEY_PAGE_SIZE, title="count of results rows", ge=1),
    page_number: int | None = Query(default=1, alias=KEY_PAGE_NUM, title="number of page (pagination)", ge=1),
    service: PersonSearchService = Depends(PersonSearchService.get_service),
) -> ServiceResult:

    param_dict = {KEY_PAGE_NUM: page_number, KEY_PAGE_SIZE: page_size, KEY_QUERY: query}
    answer = await service.get(param_dict)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="persons not found")

    return answer
