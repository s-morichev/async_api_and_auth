from uuid import UUID

from pydantic import Field

from models.base_dto import BaseDTO


class IdModel(BaseDTO):
    id: UUID = Field(..., alias="uuid")


class Genre(IdModel):
    name: str


class Film(IdModel):
    title: str


class RoleMovies(BaseDTO):
    role: str
    movies: list[Film]


class Person(BaseDTO):
    uuid: UUID
    full_name: str


class ExtendedPerson(Person):
    movies: list[RoleMovies]


class FilmImdb(IdModel):
    title: str
    imdb_rating: float


class ExtendedFilm(Film):
    description: str
    genre: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]
