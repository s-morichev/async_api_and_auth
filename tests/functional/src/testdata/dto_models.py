from uuid import UUID

from pydantic import Field

from .core_model import CoreModel


class IdModel(CoreModel):
    id: UUID = Field(..., alias="uuid")


class Genre(IdModel):
    name: str


class Film(IdModel):
    title: str


class ImdbFilm(Film):
    imdb_rating: float


class RoleMovies(CoreModel):
    role: str
    movies: list[Film]


class Person(IdModel):
    name: str = Field(..., alias="full_name")


class ExtendedPerson(Person):
    movies: list[RoleMovies]


class ExtendedFilm(Film):
    description: str
    imdb_rating: float
    fw_type: str
    rars_rating: int
    genres: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]