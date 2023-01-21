import datetime
from abc import ABC
from contextlib import closing
from typing import Callable, Iterator

import psycopg2
from psycopg2.extensions import connection as PGConnection
from psycopg2.extras import DictCursor

from core import etl_logger
from core.backoff import backoff_gen
from core.constants import (
    ENRICH_SQL,
    FILMWORK_SQL,
    FW_UPDATE_KEY,
    GENRE_SQL,
    GENRES_UPDATE_KEY,
    PERSON_SQL,
    PERSONS_UPDATE_KEY,
    MARK_SQL,
    MARKS_UPDATE_KEY,
)
from pipeline.data_classes import PGData
from pipeline.etl_pipeline import ETLData, ETLPipelineError, Extractor

logger = etl_logger.get_logger(__name__)


class ExtractorWorker(ABC):
    row_count: int = 0

    def get_data(self, connection_factory: Callable[[], PGConnection], settings: dict) -> Iterator[PGData]:
        pass


class BaseExtractorWorker(ExtractorWorker):
    state: dict = None
    STATE_KEY = "BASE_KEY"
    NAME = "BASE"
    DATA_CLASS = PGData

    def _get_sql_string(self):
        """return SQL string for query"""

    def _enrich(self, connection, data: list[dict]) -> list[dict]:
        """На вход получаем список словарей с id filmwork, на выходе готовые данные"""
        with closing(connection.cursor()) as cursor:
            ids = tuple(row["f_id"] for row in data)
            cursor.execute(ENRICH_SQL, (ids,))
            rows = cursor.fetchall()
        return rows

    def _mark_state(self, data: list[dict]):
        """mark state of Extractor if need"""
        # in filmworks id is f_id
        self.state[self.STATE_KEY] = (data[-1]["modified"], data[-1].get("id") or data[-1].get("f_id"))

    def _get_state_date(self, key: str = None) -> str | datetime.datetime:
        """return date from state if exist else return datetime.min"""
        if not key:
            key = self.STATE_KEY
        if self.state[key]:
            return self.state.get(key)[0]
        return datetime.datetime.min

    def _same_data_in_rows(self, rows: list[dict]) -> bool:
        """check if in rows last row is same as loaded"""
        if not self.state[self.STATE_KEY]:
            return False
        last_date, last_id = self.state[self.STATE_KEY]
        # may be str, cant compare
        if isinstance(last_date, str):
            last_date = datetime.datetime.fromisoformat(last_date)
        # in filmwork id is f_id
        last_row_date, last_row_id = rows[-1]["modified"], rows[-1].get("id") or rows[-1].get("f_id")
        is_same = (last_date == last_row_date) and (last_id == last_row_id)
        return is_same

    # psycopg2.DatabaseError - не стал ловить, пусть лучше вываливается и перезагружается сервис
    @backoff_gen(exceptions=(psycopg2.OperationalError,), logger_func=logger.error)
    def get_data(self, connection_factory: Callable[[], PGConnection], settings: dict) -> Iterator[ETLData]:
        logger.debug(f"{self.NAME} worker get data")
        self.state = settings["state"]
        connection = connection_factory()

        with closing(connection.cursor("ETL_DATA_CURSOR")) as cursor:
            cursor.execute(self._get_sql_string())
            while rows := cursor.fetchmany(size=settings["batch_size"]):
                # if data is loaded - do nothing
                if self._same_data_in_rows(rows):
                    logger.debug("Nothing to load")
                    return None

                enrich_rows = self._enrich(connection, rows)

                self._mark_state(rows)
                self.row_count += len(rows)
                logger.debug(f" {type(self).__name__}: load data from db row count:{len(enrich_rows)}")

                yield from [self.DATA_CLASS(**row) for row in enrich_rows]

            else:
                logger.debug("Mark no data")
                self._mark_state_no_data(connection)

    def _mark_state_no_data(self, connection: PGConnection, sql: str = ""):
        """
        save state when no data select
        it can be in Persons and Genres due optimization
        """
        if not sql:
            return

        with closing(connection.cursor()) as cursor:
            cursor.execute(sql)
            max_date = cursor.fetchone()
            if max_date:
                self._mark_state([{"modified": max_date[1], "id": max_date[0]}])


class FWExtractorWorker(BaseExtractorWorker):
    STATE_KEY = FW_UPDATE_KEY
    NAME = "Filworks Extractor"

    def _get_sql_string(self):
        fw_date = self._get_state_date()
        return FILMWORK_SQL.format(fw_date)


class PersonsExtractorWorker(BaseExtractorWorker):
    STATE_KEY = PERSONS_UPDATE_KEY
    NAME = "Persons 2M2 Extractor"

    def _get_sql_string(self):
        p_date = self._get_state_date()
        fw_date = self._get_state_date(FW_UPDATE_KEY)
        return PERSON_SQL.format(p_date, fw_date)

    def _mark_state_no_data(self, connection: PGConnection, sql: str = ""):
        sql = "Select p.id, p.modified from content.person p order by p.modified desc, p.id desc limit 1;"
        super()._mark_state_no_data(connection, sql)


class GenresExtractorWorker(BaseExtractorWorker):
    STATE_KEY = GENRES_UPDATE_KEY
    NAME = "Genres 2M2 Extractor"

    def _get_sql_string(self):
        g_date = self._get_state_date()
        fw_date = self._get_state_date(FW_UPDATE_KEY)
        return GENRE_SQL.format(g_date, fw_date)

    def _mark_state_no_data(self, connection: PGConnection, sql: str = ""):
        sql = "Select g.id, g.modified from content.genre g order by g.modified desc, g.id desc limit 1;"
        super()._mark_state_no_data(connection, sql)


class MarksExtractorWorker(BaseExtractorWorker):
    STATE_KEY = MARKS_UPDATE_KEY
    NAME = "MARK 2M2 Extractor"

    def _get_sql_string(self):
        m_date = self._get_state_date()
        fw_date = self._get_state_date(FW_UPDATE_KEY)
        return MARK_SQL.format(m_date, fw_date)

    def _mark_state_no_data(self, connection: PGConnection, sql: str = ""):
        sql = "Select m.id, m.modified from content.mark m order by m.modified desc, m.id desc limit 1;"
        super()._mark_state_no_data(connection, sql)


class FWExtractor(Extractor):
    def __init__(self, dsn: str, batch_size: int = 100):
        self.dsn: str = dsn
        self.batch_size: int = batch_size
        self.connection: PGConnection | None = None
        # Workers - собирают записи которые надо будет записать в базу
        self.workers = [PersonsExtractorWorker(), GenresExtractorWorker(), MarksExtractorWorker(), FWExtractorWorker()]

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
        settings = {"state": self.state, "batch_size": self.batch_size}
        try:
            for worker in self.workers:
                worker.row_count = 0
                yield from worker.get_data(connection_factory=self._get_connection, settings=settings)
                self.row_count += worker.row_count
        finally:
            self._close_connection()

    def pre_check(self) -> None:
        try:
            self._get_connection()
        except psycopg2.OperationalError as e:
            raise ETLPipelineError(f"PGExtractor pre_check failed. {e}") from e
        logger.info("Postgres extractor pre_check OK")
