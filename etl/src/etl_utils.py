import json

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ElasticsearchException

import etl_logger
from settings import *

logger = etl_logger.get_logger(__name__)


def es_create_index_if_not_exist(index_name: str, schema_file: str) -> bool:
    """ check if index exists and try to create them
    :return True if all OK, False if error occurred
    """
    logger.info('check ES Index...')
    try:
        logger.debug(f'ES in {settings.ES_URI}')
        es = Elasticsearch(settings.ES_URI)
        if es.indices.exists(index=index_name):
            return True

        logger.debug(f'Elasticsearch creating index "{index_name}" is not exist')

        with open(schema_file, 'r') as schema_file:
            schema = schema_file.read()
            schema_dict = json.loads(schema)
            es.indices.create(index=index_name,
                              mappings=schema_dict['mappings'],
                              settings=schema_dict.get('settings'))

    except (ElasticsearchException, FileNotFoundError) as err:
        msg = f'Elasticsearch index {index_name}  create error:{err}'
        if settings.DEBUG:
            logger.exception(msg)
        else:
            logger.error(msg)
        return False

    else:
        logger.debug(f'Elasticsearch creating index "{index_name}" is OK')
        return True


def check_or_create_indexes():
    return (
            es_create_index_if_not_exist(settings.ES_INDEX_MOVIES, SCHEMA_FILE_MOVIES) and
            es_create_index_if_not_exist(settings.ES_INDEX_PERSONS, SCHEMA_FILE_PERSONS) and
            es_create_index_if_not_exist(settings.ES_INDEX_GENRES, SCHEMA_FILE_GENRES)
            )
