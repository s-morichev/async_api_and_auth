from http import HTTPStatus
from uuid import UUID

from core.constants import KEY_PAGE_NUM, KEY_PAGE_SIZE, KEY_QUERY, KEY_ID
from fastapi import APIRouter, Depends, HTTPException, Query
from models.service_result import ServiceResult
from services.persons_search import PersonSearchService
from services.person_by_id import PersonByIdService
from services.films_by_person import FilmsByPersonService
from api.v1.schemas import ExtendedPerson, ManyExtendedPerson, ImdbFilm,  ManyImdbFilm


router = APIRouter()


@router.get("/search/{person_id}", response_model=ExtendedPerson, tags=["Персона по id"])
async def person_by_id(
        person_id: UUID, service: PersonByIdService = Depends(PersonByIdService.get_service)
) -> ExtendedPerson:
    param_dict = {KEY_ID: person_id}
    answer = await service.get(param_dict)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"person id:{person_id} not found")

    return ExtendedPerson(**answer.result.dict())


@router.get("/{person_id}/film", response_model=ManyImdbFilm, tags=["Фильмы по id персоны"])
async def films_by_person(
        person_id: UUID,
        page_size: int | None = Query(default=50, alias=KEY_PAGE_SIZE, title="count of results rows", ge=1),
        page_number: int | None = Query(default=1, alias=KEY_PAGE_NUM, title="number of page (pagination)", ge=1),
        service: FilmsByPersonService = Depends(FilmsByPersonService.get_service),
) -> ManyImdbFilm:
    param_dict = {KEY_PAGE_NUM: page_number, KEY_PAGE_SIZE: page_size, KEY_ID: person_id}

    answer = await service.get(param_dict)
    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"films for person id:{person_id} not found")
    lst_film = [ImdbFilm(**dto.dict()) for dto in answer.result]

    # вот здесь то можно и переложить данные
    return ManyImdbFilm(total=answer.total, result=lst_film)


@router.get("/", response_model=ManyExtendedPerson, tags=["Поиск персон по имени"])
async def person_search(
        query: str | None = Query(default="", alias=KEY_QUERY, title="string for search"),
        page_size: int | None = Query(default=50, alias=KEY_PAGE_SIZE, title="count of results rows", ge=1),
        page_number: int | None = Query(default=1, alias=KEY_PAGE_NUM, title="number of page (pagination)", ge=1),
        service: PersonSearchService = Depends(PersonSearchService.get_service),
) -> ManyExtendedPerson:

    param_dict = {KEY_PAGE_NUM: page_number, KEY_PAGE_SIZE: page_size, KEY_QUERY: query}
    answer = await service.get(param_dict)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"persons for '{query}' not found")

    lst_person = [ExtendedPerson(**dto.dict()) for dto in answer.result]
    return ManyExtendedPerson(total=answer.total, result=lst_person)
