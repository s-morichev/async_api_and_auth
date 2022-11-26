from datetime import datetime

from pydantic import BaseModel, validator

from etl_pipeline import ETLData


class IdNameMixin(BaseModel):
    id: str
    name: str


class Person(IdNameMixin):
    pass


class Genre(IdNameMixin):
    pass


class PersonWithRole(IdNameMixin):
    role: str


class BaseETLData(BaseModel, ETLData):
    id: str
    fw_type: str
    title: str
    description: str | None
    imdb_rating: float | None
    genres: list[Genre] | None
    modified: datetime


class PGData(BaseETLData):
    persons: list[PersonWithRole]


class ESData(BaseETLData):
    genre: list[str]

    # лучше бы назвал director_names. Но схема есть схема...
    director: list[str]
    actors_names: list[str]
    writers_names: list[str]

    actors: list[Person]
    writers: list[Person]
    directors: list[Person]

    @validator('imdb_rating')
    def validate_rating(cls, v):
        if v is None:
            return 0.0
        else:
            return v

    @validator('description')
    def validate_string_data(cls, v):
        if v:
            return v
        else:
            return ''
