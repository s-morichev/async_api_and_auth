from core.core_model import CoreModel
from fastapi import Query
from core.constants import (DEFAULT_PAGE_SIZE, KEY_PAGE_SIZE, KEY_PAGE_NUM,
                            KEY_QUERY, MAX_PAGE_SIZE, ES_PAGINATION_LIMIT)


class PageParams(CoreModel):
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, alias=KEY_PAGE_SIZE,
                           title="count of results rows", ge=1, lte=MAX_PAGE_SIZE),
    page_number: int = Query(default=1, alias=KEY_PAGE_NUM, title="number of page (pagination)", ge=1)




class QueryPageParams(PageParams):
    query: str = Query(default="", alias=KEY_QUERY, title="string for search")
