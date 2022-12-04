from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import Field
from pydantic.generics import GenericModel

from core.core_model import CoreModel

ModelT = TypeVar("ModelT")


class ManyResponse(GenericModel, Generic[ModelT]):
    total: int = Field(..., title="Amount rows in source")
    result: list[ModelT]

    @classmethod
    def __concrete_name__(cls: type[Any], params: tuple[type[Any], ...]) -> str:
        return f"{params[0].__name__.title()}ManyResponse"


class Genre(CoreModel):
    """Movies genre"""

    uuid: UUID = Field(title="id")
    name: str = Field(title="genres name")


class Film(CoreModel):
    """Film (uuid,title)"""

    uuid: UUID
    title: str = Field(title="movie title")


class Person(CoreModel):
    """Person info"""

    uuid: UUID = Field(title="person id")
    full_name: str = Field(title="persons full name")


class RoleMovies(CoreModel):
    role: str
    movies: list[Film]


class ExtendedPerson(Person):
    movies: list[RoleMovies]


class ImdbFilm(Film):
    """Film (uuid,title, imdb)"""

    imdb_rating: float = Field(title="IMDB rating")


class ExtendedImdbFilm(ImdbFilm):
    """Film with extended info"""

    description: str = Field(title="movie description")
    genres: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]
