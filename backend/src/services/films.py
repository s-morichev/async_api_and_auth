import logging
from functools import lru_cache
from typing import Any
from uuid import UUID

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models import api_models

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

logger = logging.getLogger(__name__)


class FilmService:
    """Сервис для поиска информации, связанной с фильмами"""

    INDEX_NAME = "movies"

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    def _get_search_parameters(
        self,
        search_for: str | None = None,
        sort_field: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
        filter_genre: UUID | None = None,
    ) -> dict[str, Any]:
        search_params = {"index": self.INDEX_NAME, "source_includes": ["imdb_rating", "title"], "query": {"bool": {}}}

        if search_for is None:
            search_params["query"]["bool"]["must"] = {"match_all": {}}
        else:
            search_params["query"]["bool"]["must"] = {
                "multi_match": {"query": search_for, "fields": ["title^5", "description^3", "genre"], "fuzziness": "AUTO"}
            }

        if sort_field is not None:
            search_params["sort"] = [{sort_field[1:]: {"order": "asc" if sort_field[0] == "+" else "desc"}}]

        if page_number is not None and page_size is not None:
            search_params["from"] = (page_number - 1) * page_size
            search_params["size"] = page_size

        if filter_genre is not None:
            search_params["query"]["bool"]["filter"] = {
                "nested": {
                    "path": "genres",
                    "query": {"term": {"genres.id": str(filter_genre)}}
                }
            }

        return search_params

    async def get_by_id(self, film_id: str) -> api_models.ExtendedFilm | None:
        """Получить полную информацию о конкретном фильме по id.

        Args:
            film_id: id фильма

        Returns:
            Расширенная модель фильма либо None, если фильм с таким id не найден.
        """
        cache_key = f"film id:{film_id}"
        cache_data = await self._get_from_cache(cache_key)
        if cache_data is None:
            film = await self._get_film_from_elastic(film_id)
            if film is None:
                return None
            await self._put_to_cache(cache_key, film.json())
        else:
            film = api_models.ExtendedFilm.parse_raw(cache_data)

        return film

    async def search(
        self,
        search_for: str | None = None,
        sort_field: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
        filter_genre: UUID | None = None,
    ) -> list[api_models.Film]:
        cache_key = f"film search:{search_for}:{page_number}:{page_size}:{sort_field}:{filter_genre}"
        cache_data = await self._get_from_cache(cache_key)
        if cache_data is None:
            search_parameters = self._get_search_parameters(
                search_for, sort_field, page_number, page_size, filter_genre
            )
            films_list = await self._search_elastic(search_parameters)
            await self._put_to_cache(cache_key, films_list.json())
        else:
            films_list = api_models.FilmList.parse_raw(cache_data)
        return films_list.films

    async def get_similar_by_id(
        self,
        film_id: str,
        page_number: int | None = None,
        page_size: int | None = None,
    ) -> list[api_models.Film]:
        film = await self.get_by_id(film_id=film_id)
        if film is None:
            return []
        else:
            genre_id = film.genres[0].uuid

        return await self.search(sort_field="-imdb_rating", page_number=page_number, page_size=page_size, filter_genre=genre_id)

    async def _get_film_from_elastic(self, film_id: str) -> api_models.ExtendedFilm | None:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
            logger.debug("film doc %s", doc)
        except NotFoundError:
            return None
        return api_models.ExtendedFilm(uuid=doc["_id"], **doc["_source"])

    async def _search_elastic(self, parameters) -> api_models.FilmList:

        result = await self.elastic.search(**parameters)

        films_list = [api_models.Film(uuid=doc["_id"], **doc["_source"]) for doc in result["hits"]["hits"]]
        scores = [doc["_score"] for doc in result["hits"]["hits"]]
        logger.debug("scores %s", scores)
        return api_models.FilmList(films=films_list)

    async def _put_to_cache(self, key: str, value: str) -> None:
        logger.debug("put to redis key=%s", key)
        await self.redis.set(key, value, ex=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _get_from_cache(self, key) -> str | None:
        logger.debug("get from redis key=%s", key)
        return await self.redis.get(key)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    """Получить экземпляр FilmService.

    При каждом вызове возвращается один и тот же экземпляр за счет кеширования.
    """
    return FilmService(redis, elastic)
