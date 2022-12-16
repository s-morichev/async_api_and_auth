import logging.config
from http.client import HTTPConnection

from elasticsearch import Elasticsearch

import backoff
from redis import Redis
from settings import settings

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


@backoff.on_predicate(backoff.expo, logger=logger, max_time=300, max_value=5)
def check_elasticsearch(es_client):
    return es_client.ping()


@backoff.on_predicate(backoff.expo, logger=logger, max_time=300, max_value=5)
def check_redis(redis_client):
    return redis_client.ping()


@backoff.on_predicate(backoff.expo, logger=logger, max_time=300, max_value=5)
def check_backend(backend_conn):
    try:
        backend_conn.connect()
        return True
    except ConnectionRefusedError:
        return False


def wait():
    redis_client = Redis.from_url(settings.REDIS_URI)
    check_redis(redis_client)

    es_client = Elasticsearch(settings.ES_URI)
    check_elasticsearch(es_client)

    cut_off = len("http://")
    connection = HTTPConnection(settings.API_URI[cut_off:])
    check_backend(connection)


if __name__ == "__main__":
    wait()
