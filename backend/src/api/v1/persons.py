from http import HTTPStatus
from uuid import UUID

from api.v1.schemas import ExtendedPerson, ImdbFilm, ManyResponse
from core.constants import KEY_PAGE_NUM, KEY_PAGE_SIZE, KEY_QUERY
from core.utils import validate_pagination
from fastapi import APIRouter, Depends, HTTPException, Query
from services.persons import FilmsByPersonService, PersonByIdService, PersonSearchService

router = APIRouter()


@router.get("/search/{person_id}", response_model=ExtendedPerson)
async def person_by_id(
    person_id: UUID, service: PersonByIdService = Depends(PersonByIdService.get_service)
) -> ExtendedPerson:

    answer = await service.get(person_id=person_id)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"person id:{person_id} not found")

    return ExtendedPerson(**answer.result.dict())


@router.get("/{person_id}/film", response_model=ManyResponse[ImdbFilm])
async def films_by_person(
    person_id: UUID,
    page_size: int = Query(default=50, alias=KEY_PAGE_SIZE, title="count of results rows", ge=1),
    page_number: int = Query(default=1, alias=KEY_PAGE_NUM, title="number of page (pagination)", ge=1),
    service: FilmsByPersonService = Depends(FilmsByPersonService.get_service),
) -> ManyResponse[ImdbFilm]:

    if message := validate_pagination(page_number, page_size):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=message)

    answer = await service.get(page_num=page_number, page_size=page_size, person_id=person_id)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"films for person id:{person_id} not found")

    lst_film = [ImdbFilm(**dto.dict()) for dto in answer.result]

    return ManyResponse[ImdbFilm](total=answer.total, result=lst_film)


@router.get("/", response_model=ManyResponse[ExtendedPerson])
async def person_search(
    query: str = Query(default="", alias=KEY_QUERY, title="string for search"),
    page_size: int = Query(default=50, alias=KEY_PAGE_SIZE, title="count of results rows", ge=1),
    page_number: int = Query(default=1, alias=KEY_PAGE_NUM, title="number of page (pagination)", ge=1),
    service: PersonSearchService = Depends(PersonSearchService.get_service),
) -> ManyResponse[ExtendedPerson]:

    if message := validate_pagination(page_number, page_size):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=message)

    answer = await service.get(page_num=page_number, page_size=page_size, query=query)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"persons for '{query}' not found")

    lst_person = [ExtendedPerson(**dto.dict()) for dto in answer.result]
    return ManyResponse[ExtendedPerson](total=answer.total, result=lst_person)
