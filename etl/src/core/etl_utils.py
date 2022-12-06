from json import JSONDecodeError, loads

from elastic_transport import ConnectionError
from elasticsearch import Elasticsearch

from core import etl_logger
from core.settings import SCHEMA_FILE_GENRES, SCHEMA_FILE_MOVIES, SCHEMA_FILE_PERSONS, settings

logger = etl_logger.get_logger(__name__)


def es_create_index_if_not_exist(index_name: str, schema_file: str) -> bool:
    """check if index exists and try to create them
    throw ES ConnectionError if raised

    :param index_name - index for check
    :param schema_file - file json with index schema

    :return True if all OK, False if error occurred
    """

    logger.info("check ES Index...")
    # 1. connect to ES and check index existing
    try:
        es = Elasticsearch(settings.ES_URI)
        if es.indices.exists(index=index_name):
            return True

    except ConnectionError as err:
        msg = f"No connection to Elasticsearch: {err}"
        logger.error(msg)
        raise err

    logger.debug(f'Elasticsearch creating index "{index_name}" is not exist')

    # 2. load schema from JSON file
    try:
        with open(schema_file, "r") as schema_file:
            schema = schema_file.read()
            schema_dict = loads(schema)

    except (JSONDecodeError, FileNotFoundError) as err:
        msg = f"Elasticsearch index {index_name}  create error:{err}"
        logger.error(msg)
        return False

    # 3. Check for mappings key in schema
    key_mappings = "mappings"
    if key_mappings not in schema_dict:
        msg = f"Elasticsearch index {index_name}  create error: No 'mappings' in schema file"
        logger.error(msg)
        return False

    # 4. Create index
    try:
        es.indices.create(index=index_name, mappings=schema_dict[key_mappings], settings=schema_dict.get("settings"))

    except ConnectionError as err:
        msg = f"Elasticsearch index {index_name}  create error: {err}"
        logger.error(msg)
        raise err

    logger.debug(f'Elasticsearch creating index "{index_name}" is OK')
    return True


def check_or_create_indexes():
    return (
        es_create_index_if_not_exist(settings.ES_INDEX_MOVIES, SCHEMA_FILE_MOVIES)
        and es_create_index_if_not_exist(settings.ES_INDEX_PERSONS, SCHEMA_FILE_PERSONS)
        and es_create_index_if_not_exist(settings.ES_INDEX_GENRES, SCHEMA_FILE_GENRES)
    )
