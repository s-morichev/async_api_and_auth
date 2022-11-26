import datetime
from abc import ABC
from contextlib import closing
from typing import Callable, Iterator

import psycopg2
from psycopg2.extensions import connection as PGConnection
from psycopg2.extensions import cursor as PGCursor
from psycopg2.extras import DictCursor

import etl_logger
from backoff import backoff_gen
from constants import (FW_UPDATE_KEY, GENRES_UPDATE_KEY, PERSONS_UPDATE_KEY,
                       FILMWORK_SQL, PERSON_SQL, GENRE_SQL, ENRICH_SQL)
from data_classes import PGData
from etl_pipeline import Extractor, ETLPipelineError

logger = etl_logger.get_logger(__name__)


class ExtractorWorker(ABC):
    def get_data(self, connection_factory: Callable[[], PGConnection], settings: dict) -> Iterator[PGData]:
        pass


class BaseExtractorWorker(ExtractorWorker):
    state: dict = None
    STATE_KEY = 'BASE_KEY'

    def _get_sql_string(self):
        """ return SQL string for query"""

    def _enrich(self, connection, data: list[dict]) -> list[dict]:
        """ На вход получаем список словарей с id filmwork, на выходе готовые данные"""
        with closing(connection.cursor()) as cursor:
            ids = tuple(row['id'] for row in data)
            cursor.execute(ENRICH_SQL, (ids,))
            rows = cursor.fetchall()
        return rows


    def _mark_state(self, data: list[dict]):
        """ mark state of Extractor if need"""
        self.state[self.STATE_KEY] = data[-1]['modified']

    # psycopg2.DatabaseError - не стал ловить, пусть лучше вываливается и перезагружается сервис
    @backoff_gen(exceptions=(psycopg2.OperationalError,), logger_func=logger.error)
    def get_data(self, connection_factory: Callable[[], PGConnection], settings: dict) -> Iterator[PGData]:
        self.state = settings['state']
        connection = connection_factory()

        with closing(connection.cursor()) as cursor:
            cursor.execute(self._get_sql_string())
            while rows := cursor.fetchmany(size=settings['batch_size']):
                enrich_rows = self._enrich(connection, rows)
                self._mark_state(rows)
                logger.debug(f' {type(self).__name__}: load data from db row count:{len(enrich_rows)}')
                yield from [PGData(**row) for row in enrich_rows]
            else:
                self._mark_state_no_data(cursor)

    def _mark_state_no_data(self, cursor: PGCursor):
        """
        save state when no data select
        it can be in Persons and Genres due optimization
        """


class FWExtractorWorker(BaseExtractorWorker):
    STATE_KEY = FW_UPDATE_KEY

    def _get_sql_string(self):
        fw_date = (self.state.get(self.STATE_KEY) or datetime.datetime.min)
        return FILMWORK_SQL.format(fw_date)


class PersonsExtractorWorker(BaseExtractorWorker):
    STATE_KEY = PERSONS_UPDATE_KEY

    def _get_sql_string(self):
        p_date = (self.state.get(self.STATE_KEY) or datetime.datetime.min)
        fw_date = (self.state.get(FW_UPDATE_KEY) or datetime.datetime.min)
        return PERSON_SQL.format(p_date, fw_date)

    def _mark_state_no_data(self, cursor: PGCursor):
        cursor.execute("select max(p.modified) from content.person p")
        max_date = cursor.fetchone()
        if max_date:
            self._mark_state([{'modified': max_date[0]}])


class GenresExtractorWorker(BaseExtractorWorker):
    STATE_KEY = GENRES_UPDATE_KEY

    def _get_sql_string(self):
        g_date = (self.state.get(self.STATE_KEY) or datetime.datetime.min)
        fw_date = (self.state.get(FW_UPDATE_KEY) or datetime.datetime.min)
        return GENRE_SQL.format(g_date, fw_date)

    def _mark_state_no_data(self, cursor: PGCursor):
        cursor.execute("select max(g.modified) from content.genre g")
        max_date = cursor.fetchone()
        if max_date:
            self._mark_state([{'modified': max_date[0]}])


class PGExtractor(Extractor):
    def __init__(self, dsn: str, batch_size: int = 100):
        self.dsn: str = dsn
        self.batch_size: int = batch_size
        self.connection: PGConnection | None = None
        self.workers = [PersonsExtractorWorker(), GenresExtractorWorker(), FWExtractorWorker()]

    def _get_connection(self) -> PGConnection:
        if self.connection and not self.connection.closed:
            return self.connection
        else:
            self.connection = psycopg2.connect(self.dsn, cursor_factory=DictCursor)
            return self.connection

    def _close_connection(self):
        if self.connection:
            self.connection.close()

    def get_data(self) -> Iterator[PGData]:
        settings = {'state': self.state, 'batch_size': self.batch_size}
        try:
            for worker in self.workers:
                yield from worker.get_data(connection_factory=self._get_connection, settings=settings)
        finally:
            self._close_connection()

    def pre_check(self) -> None:
        try:
            self._get_connection()
        except psycopg2.OperationalError as e:
            raise ETLPipelineError(f'PGExtractor pre_check failed. {e}') from e
        logger.info('Postgres extractor pre_check OK')
