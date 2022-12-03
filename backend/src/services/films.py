from uuid import UUID

from core.constants import ES_MOVIES_INDEX
from core.service_logger import get_logger
from elasticsearch import NotFoundError
from models import dto_models
from models.service_result import ServiceListResult, ServiceSingeResult
from services.base_service import BaseService

logger = get_logger(__name__)


class PopularFilmsService(BaseService):
    """Популярные фильмы."""

    NAME = "POPULAR_FILMS"
    RESULT_MODEL = ServiceListResult[dto_models.ImdbFilm]

    async def get_from_elastic(
        self,
        *,
        sort_by: str,
        genre_id: UUID,
        page_number: int,
        page_size: int,
    ) -> "PopularFilmsService.RESULT_MODEL | None":
        query = {"bool": {"must": {"match_all": {}}}}
        if genre_id is not None:
            filter_genre = {"filter": {"nested": {"path": "genres", "query": {"term": {"genres.id": str(genre_id)}}}}}
            query["bool"].update(filter_genre)

        sort_order = "asc" if sort_by[0] == "+" else "desc"
        sort = [{sort_by[1:]: {"order": sort_order}}]

        es = {
            "index": ES_MOVIES_INDEX,
            "from_": (page_number - 1) * page_size,
            "size": page_size,
            "source_includes": ["imdb_rating", "title"],
            "query": query,
            "sort": sort,
        }

        try:
            response = await self.elastic.search(**es)
        except NotFoundError:
            return None

        total = response["hits"]["total"]["value"]
        results_list = [self.BASE_MODEL(uuid=doc["_id"], **doc["_source"]) for doc in response["hits"]["hits"]]

        result = self.RESULT_MODEL(total=total, page_num=page_number, page_size=page_size, result=results_list)
        return result


class SearchFilmsService(BaseService):
    """Поиск фильмов."""

    NAME = "SEARCH_FILMS"
    RESULT_MODEL = ServiceListResult[dto_models.ImdbFilm]

    async def get_from_elastic(
        self,
        *,
        search_for: str,
        genre_id: UUID,
        page_number: int,
        page_size: int,
    ) -> "SearchFilmsService.RESULT_MODEL | None":
        query = {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": search_for,
                        "fields": ["title^5", "description^3", "genre"],
                        "fuzziness": "AUTO",
                    }
                }
            }
        }
        if genre_id is not None:
            filter_genre = {"filter": {"nested": {"path": "genres", "query": {"term": {"genres.id": str(genre_id)}}}}}
            query["bool"].update(filter_genre)

        es = {
            "index": ES_MOVIES_INDEX,
            "from_": (page_number - 1) * page_size,
            "size": page_size,
            "source_includes": ["imdb_rating", "title"],
            "query": query,
        }

        try:
            response = await self.elastic.search(**es)
        except NotFoundError:
            return None

        total = response["hits"]["total"]["value"]
        results_list = [self.BASE_MODEL(uuid=doc["_id"], **doc["_source"]) for doc in response["hits"]["hits"]]

        result = self.RESULT_MODEL(total=total, page_num=page_number, page_size=page_size, result=results_list)
        return result


class FilmByIdService(BaseService):
    """Фильм по id."""

    NAME = "FILM_BY_ID"
    RESULT_MODEL = ServiceSingeResult[dto_models.ExtendedFilm]

    async def get_from_elastic(self, *, film_id: UUID) -> "FilmByIdService.RESULT_MODEL | None":
        try:
            response = await self.elastic.get(index=ES_MOVIES_INDEX, id=str(film_id))
        except NotFoundError:
            return None

        result = dto_models.ExtendedFilm(uuid=response["_id"], **response["_source"])

        result = self.RESULT_MODEL(total=1, page_num=1, page_size=1, result=result)
        return result


class SimilarFilmsService(BaseService):
    """Похожие фильмы."""

    NAME = "SIMILAR_FILMS"
    RESULT_MODEL = ServiceListResult[dto_models.ImdbFilm]

    async def get_from_elastic(
        self,
        *,
        film_id: UUID,
        page_number: int,
        page_size: int,
    ) -> "SimilarFilmsService.RESULT_MODEL | None":
        resp = await (await FilmByIdService.get_service()).get_from_elastic(film_id=film_id)
        if resp is None:
            return None
        if resp.result.genres:
            genre_id = resp.result.genres[0].uuid

        result = await (await PopularFilmsService.get_service()).get_from_elastic(
            sort_by="-imdb_rating", genre_id=genre_id, page_number=page_number, page_size=page_size
        )

        return result
