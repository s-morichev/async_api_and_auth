from uuid import UUID

from models.mixins import BaseOrjsonModel, IdMixin


class Genre(IdMixin, BaseOrjsonModel):
    name: str


class RoleMovies(BaseOrjsonModel):
    role: str
    movies: list[UUID]


class Person(IdMixin, BaseOrjsonModel):
    full_name: str


class ExtendedPerson(Person):
    movies: list[RoleMovies]


class Film(IdMixin, BaseOrjsonModel):
    title: str
    imdb_rating: float


class ExtendedFilm(Film):
    description: str
    genre: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]
