import logging
from abc import abstractmethod
from typing import TypeVar
from uuid import UUID

from elasticsearch import AsyncElasticsearch, ConnectionError, NotFoundError

from core.constants import ES_GENRES_INDEX, ES_MOVIES_INDEX, ES_PERSONS_INDEX
from core.exceptions import DatabaseConnectionError
from core.singletone import Singleton
from models.dto_models import ExtendedFilm, ExtendedPerson, Genre, IdModel, ImdbFilm

ModelT = TypeVar("ModelT", bound=IdModel)


logger = logging.getLogger(__name__)


class BaseDatabaseService(metaclass=Singleton):
    """Абстрактный класс для базы данных"""

    @abstractmethod
    async def films_all(
        self, sort_by: str, page_size: int, page_number: int, genre_id: UUID | None = None
    ) -> tuple[int, list[ImdbFilm]]:
        pass

    @abstractmethod
    async def films_search(
        self, search_for: str, page_size: int, page_number: int, genre_id: UUID | None = None
    ) -> tuple[int, list[ImdbFilm]]:
        pass

    @abstractmethod
    async def film_by_id(self, id_: UUID) -> ExtendedFilm | None:
        pass

    @abstractmethod
    async def genres_all(self, page_size: int, page_number: int) -> tuple[int, list[Genre]]:
        pass

    @abstractmethod
    async def genre_by_id(self, id_: UUID) -> Genre | None:
        pass

    @abstractmethod
    async def persons_search(
        self, search_for: str, page_size: int, page_number: int
    ) -> tuple[int, list[ExtendedPerson]]:
        pass

    @abstractmethod
    async def person_by_id(self, id_: UUID) -> ExtendedPerson | None:
        pass

    @abstractmethod
    async def person_films(self, id_: UUID, page_size: int, page_number: int) -> tuple[int, list[ImdbFilm]]:
        pass

    @abstractmethod
    async def ping(self) -> bool:
        """True if available"""


class ESDatabaseService(BaseDatabaseService):
    elastic: AsyncElasticsearch

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic
        logger.debug("create elasticsearch")

    async def ping(self) -> bool:
        """True if available"""
        return await self.elastic.ping()

    async def _process_many_docs_query(self, model: type[ModelT], es_query_params: dict) -> tuple[int, list[ModelT]]:
        try:
            response = await self.elastic.search(**es_query_params)
        except ConnectionError as err:
            raise DatabaseConnectionError("Cannot connect to elasticsearch") from err

        total = response["hits"]["total"]["value"]
        result = [model(uuid=doc["_id"], **doc["_source"]) for doc in response["hits"]["hits"]]
        return total, result

    async def _process_single_doc_query(self, model: type[ModelT], es_query_params: dict) -> ModelT | None:
        try:
            response = await self.elastic.get(**es_query_params)
            logger.debug("RESPONSE SOURCE %s", response["_source"])
        except NotFoundError:
            return None
        except ConnectionError as err:
            raise DatabaseConnectionError(f"Cannot connect to elasticsearch {self.elastic}") from err

        return model(uuid=response["_id"], **response["_source"])

    async def films_all(
        self, sort_by: str, page_size: int, page_number: int, genre_id: UUID | None = None
    ) -> tuple[int, list[ImdbFilm]]:
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

        return await self._process_many_docs_query(ImdbFilm, es)

    async def films_search(
        self, search_for: str, page_size: int, page_number: int, genre_id: UUID | None = None
    ) -> tuple[int, list[ImdbFilm]] | None:
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
        return await self._process_many_docs_query(ImdbFilm, es)

    async def film_by_id(self, id_: UUID) -> ExtendedFilm | None:
        es = {
            "index": ES_MOVIES_INDEX,
            "id": str(id_),
        }
        return await self._process_single_doc_query(ExtendedFilm, es)

    async def genres_all(self, page_size: int, page_number: int) -> tuple[int, list[Genre]]:
        es = {
            "index": ES_GENRES_INDEX,
            "from": (page_number - 1) * page_size,
            "size": page_size,
            "query": {"match_all": {}},
        }
        return await self._process_many_docs_query(Genre, es)

    async def genre_by_id(self, id_: UUID) -> Genre | None:
        es = {
            "index": ES_GENRES_INDEX,
            "id": str(id_),
        }
        return await self._process_single_doc_query(Genre, es)

    async def persons_search(
        self, search_for: str, page_size: int, page_number: int
    ) -> tuple[int, list[ExtendedPerson]]:
        es = {
            "index": ES_PERSONS_INDEX,
            "from": (page_number - 1) * page_size,
            "size": page_size,
            "query": {"match": {"full_name": {"query": search_for, "fuzziness": "AUTO"}}},
        }
        return await self._process_many_docs_query(ExtendedPerson, es)

    async def person_by_id(self, id_: UUID) -> ExtendedPerson | None:
        es = {
            "index": ES_PERSONS_INDEX,
            "id": str(id_),
        }
        return await self._process_single_doc_query(ExtendedPerson, es)

    async def person_films(self, id_: UUID, page_size: int, page_number: int) -> tuple[int, list[ImdbFilm]]:
        es = {
            "index": ES_MOVIES_INDEX,
            "from": (page_number - 1) * page_size,
            "size": page_size,
            "sort": [{"imdb_rating": {"order": "desc"}}],
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"bool": {"filter": {"term": {"actors.id": str(id_)}}}},
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"bool": {"filter": {"term": {"directors.id": str(id_)}}}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"bool": {"filter": {"term": {"writers.id": str(id_)}}}},
                            }
                        },
                    ]
                }
            },
        }
        return await self._process_many_docs_query(ImdbFilm, es)
