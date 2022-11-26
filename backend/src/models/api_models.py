import uuid

from models.mixins import BaseMixin, IdMixin


class Genre(IdMixin):
    name: str


class RoleMovies(BaseMixin):
    role: str
    movies: list[uuid.UUID]


class Person(IdMixin):
    full_name: str


class ExtendedPerson(Person):
    full_name: str
    movies: list[RoleMovies]


class Film(IdMixin):
    title: str
    imdb_rating: float


class ExtendedFilm(Film):
    description: str
    genre: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]
