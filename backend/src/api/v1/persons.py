from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api.v1.params import PageParams, QueryPageParams
from api.v1.schemas import ExtendedPerson, ImdbFilm, ManyResponse
from services.persons import FilmsByPersonService, PersonByIdService, PersonSearchService

router = APIRouter()


@router.get(
    "/search", response_model=ManyResponse[ExtendedPerson], summary="get many persons with full name like :query_string"
)
async def person_search(
    params: QueryPageParams = Depends(),
    service: PersonSearchService = Depends(PersonSearchService.get_service),
) -> ManyResponse[ExtendedPerson]:
    """
    Поиск персон по имени
    - query - поисковая строка
    - **page[number]**: номер страницы
    - **page[size]**: количество записей на странице
    """

    params.check_pagination()

    answer = await service.get(page_num=params.page_number, page_size=params.page_size, query=params.query)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"persons for '{params.query}' not found")

    lst_person = [ExtendedPerson(**dto.dict()) for dto in answer.result]
    return ManyResponse[ExtendedPerson](total=answer.total, result=lst_person)


@router.get("/{person_id}", response_model=ExtendedPerson, summary="get one person by id=:person_id")
async def person_by_id(
    person_id: UUID, service: PersonByIdService = Depends(PersonByIdService.get_service)
) -> ExtendedPerson:
    """Поиск персоны по id"""

    answer = await service.get(person_id=person_id)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"person id:{person_id} not found")

    return ExtendedPerson(**answer.result.dict())


@router.get(
    "/{person_id}/film", response_model=ManyResponse[ImdbFilm], summary="get many films by person id=:person_id"
)
async def films_by_person(
    person_id: UUID,
    params: PageParams = Depends(),
    service: FilmsByPersonService = Depends(FilmsByPersonService.get_service),
) -> ManyResponse[ImdbFilm]:

    """
    Поиск фильмов по id персоны
    - **page[number]**: номер страницы
    - **page[size]**: количество записей на странице
    """
    params.check_pagination()

    answer = await service.get(page_num=params.page_number, page_size=params.page_size, person_id=person_id)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"films for person id:{person_id} not found")

    lst_film = [ImdbFilm(**dto.dict()) for dto in answer.result]

    return ManyResponse[ImdbFilm](total=answer.total, result=lst_film)
