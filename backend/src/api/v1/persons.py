from http import HTTPStatus
from uuid import UUID

from api.v1.schemas import ExtendedPerson, ImdbFilm, ManyResponse
from core.constants import KEY_PAGE_NUM, KEY_PAGE_SIZE, KEY_QUERY, MAX_PAGE_SIZE, DEFAULT_PAGE_SIZE
from core.utils import validate_pagination
from fastapi import APIRouter, Depends, HTTPException, Query
from services.persons import FilmsByPersonService, PersonByIdService, PersonSearchService
from params import QueryPageParams, PageParams

router = APIRouter()


@router.get("/search/{person_id}", response_model=ExtendedPerson)
async def person_by_id(
    person_id: UUID, service: PersonByIdService = Depends(PersonByIdService.get_service)
) -> ExtendedPerson:
    """Поиск персоны по id"""

    answer = await service.get(person_id=person_id)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"person id:{person_id} not found")

    return ExtendedPerson(**answer.result.dict())


@router.get("/{person_id}/film", response_model=ManyResponse[ImdbFilm])
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
    if message := validate_pagination(params.page_number, params.page_size):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=message)

    answer = await service.get(page_num=params.page_number, page_size=params.page_size, person_id=person_id)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"films for person id:{person_id} not found")

    lst_film = [ImdbFilm(**dto.dict()) for dto in answer.result]

    return ManyResponse[ImdbFilm](total=answer.total, result=lst_film)


@router.get("/", response_model=ManyResponse[ExtendedPerson])
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

    if message := validate_pagination(params.page_number, params.page_size):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=message)

    answer = await service.get(page_num=params.page_number, page_size=params.page_size, query=params.query)

    if not answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"persons for '{params.query}' not found")

    lst_person = [ExtendedPerson(**dto.dict()) for dto in answer.result]
    return ManyResponse[ExtendedPerson](total=answer.total, result=lst_person)
