from abc import ABC, abstractmethod
from typing import Iterator

import etl_logger
from storage import BaseStorage, DictState

logger = etl_logger.get_logger(__name__)


class ETLData(ABC):
    """ abstract data class for ETL"""


class PipelineItem(ABC):
    """ Abstract class for pipeline items"""

    # dict object from Pipeline
    # it loads on start and is saved every execute loop
    state: dict = None

    # это не абстрактный метод, а минимальная реализация:)
    def pre_check(self) -> None:
        """ Check conditions for further work """


class Extractor(PipelineItem):
    """ abstract class for extracting data """

    @abstractmethod
    def get_data(self) -> Iterator[ETLData]:
        pass


class Transformer(PipelineItem):
    """ abstract class for transforming data """

    @abstractmethod
    def transform_data(self, data: Iterator[ETLData]) -> Iterator[ETLData]:
        pass


class Loader(PipelineItem):
    """ abstract class for loading data """

    @abstractmethod
    def load_data(self, data: Iterator[ETLData]) -> Iterator[dict]:
        pass


class ETLPipelineError(Exception):
    """Exception class for errors in pipeline"""


class ETLPipeline:
    def __init__(self, extractor: Extractor, transformer: Transformer, loader: Loader, storage: BaseStorage = None):
        self.state = DictState(storage, save_on_set=False)

        self.extractor = extractor
        self.extractor.state = self.state

        self.transformer = transformer
        self.transformer.state = self.state

        self.loader = loader
        self.loader.state = self.state

    def terminator(self, result: Iterator[dict]):
        """
        for every bulk in es_loader call save_state
        """
        for record in result:
            logger.debug(record)
        self.save_state()

    def save_state(self):
        self.state.save_state()

    def pre_check(self):
        self.extractor.pre_check()
        self.transformer.pre_check()
        self.loader.pre_check()

        logger.debug('pre_check() passed -  all OK')

    def execute(self):
        """
        run steep for ETL pipeline
        """
        db_data = self.extractor.get_data()
        transform_data = self.transformer.transform_data(db_data)
        state_data = self.loader.load_data(transform_data)
        self.terminator(state_data)

        self.save_state()
