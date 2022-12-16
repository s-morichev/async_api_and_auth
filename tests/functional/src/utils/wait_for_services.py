import backoff
from http.client import HTTPConnection
import logging

from elasticsearch import Elasticsearch
from redis import Redis

from settings import settings

logger = logging.getLogger(__name__)


@backoff.on_predicate(backoff.expo, logger=logger, max_value=5)
def check_elasticsearch(es_client):
    return es_client.ping()


@backoff.on_predicate(backoff.expo, logger=logger, max_value=5)
def check_redis(redis_client):
    return redis_client.ping()


@backoff.on_predicate(backoff.expo, logger=logger, max_value=5)
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