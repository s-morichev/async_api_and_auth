from dataclasses import dataclass
from http import HTTPStatus

from fastapi import HTTPException, Query

from core.constants import DEFAULT_PAGE_SIZE, KEY_PAGE_NUM, KEY_PAGE_SIZE, KEY_QUERY, MAX_PAGE_SIZE
from core.utils import validate_pagination


@dataclass
class PageParams:
    page_number: int = Query(default=1, alias=KEY_PAGE_NUM, title="number of page (pagination)", ge=1)
    page_size: int = Query(
        default=DEFAULT_PAGE_SIZE, alias=KEY_PAGE_SIZE, title="count of results rows", ge=1, le=MAX_PAGE_SIZE
    )

    def check_pagination(self):
        if message := validate_pagination(self.page_number, self.page_size):
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=message)


@dataclass
class QueryPageParams(PageParams):
    query: str = Query(default="", alias=KEY_QUERY, title="string for search")
