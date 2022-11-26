from pg_extractor import BaseExtractorWorker, FWExtractor
from etl_pipeline import Transformer, ETLData
from constants import EX_PERSON_UPDATE_KEY, EX_PERSONS_SQL, EX_GENRE_UPDATE_KEY, EX_GENRES_SQL
from typing import Iterator
from data_classes import FGenre, FPerson


class PersonsExtractorWorker(BaseExtractorWorker):
    """ class for Person table extract"""
    DATA_CLASS = FPerson
    STATE_KEY = EX_PERSON_UPDATE_KEY
    NAME = 'Persons Extractor'

    def _get_sql_string(self):
        person_date = self._get_state_date()
        return EX_PERSONS_SQL.format(person_date)

    def _enrich(self, connection, data: list[dict]) -> list[dict]:
        """do nothing"""
        return data


class GenresExtractorWorker(BaseExtractorWorker):
    """ class for Genre table extract"""
    DATA_CLASS = FGenre
    STATE_KEY = EX_GENRE_UPDATE_KEY
    NAME = 'Genres Extractor'

    def _get_sql_string(self):
        person_date = self._get_state_date()
        return EX_GENRES_SQL.format(person_date)

    def _enrich(self, connection, data: list[dict]) -> list[dict]:
        """do nothing"""
        return data


class DummyTransformer(Transformer):
    def transform_data(self, data: Iterator[ETLData]) -> Iterator[ETLData]:
        return data


class PersonExtractor(FWExtractor):
    def __init__(self, dsn: str, batch_size: int = 100):
        super().__init__(dsn, batch_size)
        self.workers = [PersonsExtractorWorker()]


class GenreExtractor(FWExtractor):
    def __init__(self, dsn: str, batch_size: int = 100):
        super().__init__(dsn, batch_size)
        self.workers = [GenresExtractorWorker()]

