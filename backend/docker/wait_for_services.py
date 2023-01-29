import logging.config
import os

from elasticsearch import Elasticsearch

import backoff
from redis import Redis, RedisError

REDIS_URI = os.getenv("REDIS_BACKEND_DSN")
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
def check_elasticsearch(es_client: Elasticsearch) -> bool:
    return es_client.ping()


@backoff.on_predicate(backoff.expo, logger=logger, max_time=300, on_giveup=fake_send_email, max_value=5)
def check_redis(redis_client: Redis) -> bool:
    try:
        return redis_client.ping()
    except RedisError:
        return False


def wait():
    redis_client = Redis.from_url(REDIS_URI)
    check_redis(redis_client)

    es_client = Elasticsearch(ES_URI)
    check_elasticsearch(es_client)


if __name__ == "__main__":
    wait()
