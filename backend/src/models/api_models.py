import uuid
from mixins import BaseMixin


class Genre(BaseMixin):
    name: str


class Person(BaseMixin):
    full_name: str


class ExtendedPerson(Person):
    role: str
    film_ids: list[uuid.UUID]


class Film(BaseMixin):
    title: str
    imdb_rating: float


class ExtendedFilm(Film):
    description: str
    genre: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]
