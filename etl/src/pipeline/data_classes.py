from datetime import datetime

from pydantic import BaseModel, Field, validator

from pipeline.etl_pipeline import ETLData


class IdNameMixin(BaseModel):
    id: str
    name: str


class Person(IdNameMixin):
    pass


class Movie(BaseModel):
    id: str
    title: str


class RoleMovies(BaseModel):
    role: str
    movies: list[Movie]


class FPerson(BaseModel, ETLData):
    """class for load persons directly"""

    id: str
    full_name: str
    modified: datetime
    movies: list[RoleMovies]


class FGenre(BaseModel, ETLData):
    """class for load genres directly"""

    id: str
    name: str
    modified: datetime


class Genre(IdNameMixin):
    pass


class Mark(IdNameMixin):
    pass


class PersonWithRole(IdNameMixin):
    role: str


class BaseETLData(BaseModel, ETLData):
    id: str
    fw_type: str
    rars_rating: int = Field(alias="age_limit")
    title: str
    description: str | None
    imdb_rating: float | None
    genres: list[Genre] | None
    marks: list[Mark] | None
    modified: datetime

    class Config:
        allow_population_by_field_name = True


class PGData(BaseETLData):
    persons: list[PersonWithRole]


class ESData(BaseETLData):
    genre: list[str]
    mark: list[str]
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]

    actors: list[Person]
    writers: list[Person]
    directors: list[Person]

    @validator("imdb_rating")
    def validate_rating(cls, v):
        if v is None:
            return 0.0
        else:
            # imdb rating only one digit in fractional
            return round(v, 1)

    @validator("description")
    def validate_string_data(cls, v):
        if v:
            return v
        else:
            return ""
