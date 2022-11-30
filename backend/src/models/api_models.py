from uuid import UUID

from models.mixins import BaseOrjsonModel, IdMixin
from pydantic import Field


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
