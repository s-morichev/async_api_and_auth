from typing import Any, Iterator

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ElasticsearchException
from elasticsearch.helpers import bulk

from data_classes import ESData
from backoff import backoff
from constants import DATA_COUNT_KEY
from etl_pipeline import ETLPipelineError, Loader
import etl_logger

logger = etl_logger.get_logger(__name__)


class ESLoader(Loader):
    def __init__(self, url: str, index_name: str, batch_size: int = 1000, exclude={'modified'}):
        self.url = url
        self.index_name = index_name
        self.batch_size = batch_size
        self.connection = None
        self.exclude = exclude

    def _get_connection(self):
        if self.connection:
            return self.connection
        else:
            self.connection = Elasticsearch(self.url)
            return self.connection

    @backoff(exceptions=(ElasticsearchException,), logger_func=logger.error)
    def _load_to_es(self, data: list[dict]) -> tuple:
        es = self._get_connection()
        result = bulk(es, data)
        return result

    def load_data(self, transform_data: Iterator[ESData]) -> Iterator[dict]:
        def make_portion_for_es(es_data: Iterator[ESData]) -> Iterator[list[dict[str, Any]]]:
            """ split all data in portion size of butch_size"""
            result = []
            for row in es_data:
                doc = {"_index": self.index_name, "_id": row.id, "_source": row.dict(exclude=self.exclude)}
                result.append(doc)
                if len(result) >= self.batch_size:
                    yield result
                    result = []
            else:
                if result:
                    yield result

        for data in make_portion_for_es(transform_data):
            data_count = len(data)

            self._load_to_es(data)
            logger.debug(f'es load data count:{data_count}')

            # just for info
            self.state[DATA_COUNT_KEY] += data_count
            yield {'loaded': self.state[DATA_COUNT_KEY]}

    def _index_exists(self, index_name: str):
        es = self._get_connection()
        return es.indices.exists(index=index_name)

    def ping(self) -> bool:
        es = self._get_connection()
        return es.ping()

    def pre_check(self) -> None:
        try:
            if not self.ping():
                raise ETLPipelineError(' Ping to Elasticsearch failed')
            logger.debug('Elasticsearch ping is OK')

            if not self._index_exists(self.index_name):
                raise ETLPipelineError(f'Elasticsearch index {self.index_name} not exists')

        except ElasticsearchException as e:
            raise ETLPipelineError(f'Elasticsearch pre_check error:{e}') from e

        logger.debug(f'Elasticsearch index: {self.index_name} exist')
        logger.info('Elasticsearch pre_check OK')

        #counter for data loaded
        self.state[DATA_COUNT_KEY] = 0

