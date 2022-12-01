from models.base_dto import BaseDTO
from pydantic import Field
from uuid import UUID


class ManyResponse(BaseDTO):
    """Base answer with many rows"""
    total: int = Field(..., title='Amount rows in source')
    result: list[BaseDTO]


class Genre(BaseDTO):
    """Movies genre"""
    uuid: UUID = Field(title='id')
    name: str = Field(title='genres name')


class ManyGenre(ManyResponse):
    """List of genres"""
    result: list[Genre] = Field(title='list of genres')


class Film(BaseDTO):
    uuid: UUID
    title: str = Field(title='movie title')


class Person(BaseDTO):
    """Person info"""
    uuid: UUID = Field(title='person id')
    full_name: str = Field(title='persons full name')


class RoleMovies(BaseDTO):
    role: str
    movies: list[Film]


class ExtendedPerson(Person):
    movies: list[RoleMovies]


class ManyExtendedPerson(ManyResponse):
    result: list[ExtendedPerson] = Field(title='list of persons')


class ImdbFilm(Film):
    imdb_rating: float = Field(title='IMDB rating')


class ExtendedFilm(Film):
    description: str = Field(title='movie description')
    genres: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]


class ManyFilm(ManyResponse):
    result: list[Film]


class ManyImdbFilm(ManyResponse):
    result: list[ImdbFilm]


class ManyExtendedFilm(ManyResponse):
    result: list[ExtendedFilm]