import os
import logging.config

from psycopg2 import connect, OperationalError
from elasticsearch import Elasticsearch

import backoff

PG_URI = os.getenv("PG_MOVIES_DSN")
ES_URI = os.getenv("ELK_MOVIES_DSN")


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": logging.DEBUG,
        "formatter": "default",
        "handlers": ["default"],
    },
}

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def fake_send_email(details: dict):
    logger.debug("Send email")


@backoff.on_predicate(backoff.expo, logger=logger, max_time=300, on_giveup=fake_send_email, max_value=5)
def check_postgres(pg_uri: str) -> bool:
    try:
        with connect(pg_uri) as pg_conn:
            with pg_conn.cursor() as cursor:
                cursor.execute('SELECT 1')
                return True
    except OperationalError:
        return False


@backoff.on_predicate(backoff.expo, logger=logger, max_time=300, on_giveup=fake_send_email, max_value=5)
def check_elasticsearch(es_client: Elasticsearch) -> bool:
    return es_client.ping()


def wait():
    es_client = Elasticsearch(ES_URI)
    check_elasticsearch(es_client)

    check_postgres(PG_URI)


if __name__ == "__main__":
    wait()
