import json

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ElasticsearchException

import etl_logger
from settings import settings, ES_SCHEMA_FILE

logger = etl_logger.get_logger(__name__)


def es_create_index_if_not_exist() -> bool:
    """ check if index exists and try to create them
    :return True if all OK, False if error occurred
    """
    logger.info('check ES Index...')
    try:
        logger.info(f'URI {settings.ES_URI}')
        es = Elasticsearch(settings.ES_URI)
        if es.indices.exists(index=settings.ES_INDEX_MOVIES):
            return True

        logger.debug(f'Elasticsearch creating index "{settings.ES_INDEX_MOVIES}" is not exist')

        with open(ES_SCHEMA_FILE, 'r') as schema_file:
            schema = schema_file.read()
            schema_dict = json.loads(schema)
            es.indices.create(index=settings.ES_INDEX_MOVIES,
                              mappings=schema_dict['mappings'],
                              settings=schema_dict['settings'])

    except (ElasticsearchException, FileNotFoundError) as err:
        msg = f'Elasticsearch index {settings.ES_INDEX_MOVIES}  create error:{err}'
        if settings.DEBUG:
            logger.exception(msg)
        else:
            logger.error(msg)
        return False

    else:
        logger.debug(f'Elasticsearch creating index "{settings.ES_INDEX_MOVIES}" is OK')
        return True
