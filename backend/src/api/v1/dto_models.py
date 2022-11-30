from uuid import UUID

import orjson
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    """Сериализует объект в строку JSON."""
    return orjson.dumps(v, default=default).decode(encoding="utf8")


class BaseOrjsonModel(BaseModel):
    """Базовый класс моделей, использует orjson для (де)сериализации."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        allow_population_by_field_name = True


class IdMixin(BaseModel):
    uuid: UUID


class Genre(IdMixin, BaseOrjsonModel):
    name: str


class RoleMovies(BaseOrjsonModel):
    role: str
    movies: list[UUID]


class Person(IdMixin, BaseOrjsonModel):
    full_name: str = Field(alias="name")


class ExtendedPerson(Person):
    movies: list[RoleMovies]


class Film(IdMixin, BaseOrjsonModel):
    title: str
    imdb_rating: float


class FilmList(BaseOrjsonModel):
    films: list[Film]


class ExtendedFilm(Film):
    description: str
    genres: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]
