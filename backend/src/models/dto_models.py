from uuid import UUID

from models.base_dto import BaseDTO
from pydantic import Field


class IdModel(BaseDTO):
    uuid: UUID = Field(..., alias="id")


class Genre(IdModel):
    name: str


class Film(IdModel):
    title: str


class ImdbFilm(Film):
    imdb_rating: float


class RoleMovies(BaseDTO):
    role: str
    movies: list[Film]


class Person(IdModel):
    full_name: str = Field(..., alias="name")


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
