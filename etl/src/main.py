from datetime import datetime
from threading import Event

from elastic_transport import ConnectionError as ESConnectionError

from core import etl_logger
from core.backoff import backoff
from pipeline.es_loader import ESLoader
from pipeline.etl_pipeline import ETLPipeline, ETLPipelineError
from pipeline.etl_transformer import ETLTransformer
from core.etl_utils import check_or_create_indexes
from pipeline.pg_extractor import FWExtractor
from pipeline.plane_pipelines import DummyTransformer, GenreExtractor, PersonExtractor
from core.settings import STATE_FILE, settings
from core.storage import DictState, JsonFileStorage

logger = etl_logger.get_logger("ETL")
ev_exit = Event()


@backoff(exceptions=(ESConnectionError,), logger_func=logger.error)
def all_ready_for_etl() -> bool:
    return check_or_create_indexes()


def run(pipelines: list[ETLPipeline]):
    while not ev_exit.is_set():
        loaded = 0
        logger.info("Start working...")
        start_time = datetime.now()

        for pipeline in pipelines:
            logger.info("-------------------------------------------------")
            pipeline.execute()
            logger.info(f"record loaded:{pipeline.records_loaded}")
            loaded += pipeline.records_loaded
        end_time = datetime.now()

        logger.info("-------------------------------------------------")
        logger.info(f"ETL executed. Time elapsed:{end_time - start_time}")
        logger.info(f"Amount record loaded:{loaded}")

        logger.info(f"wait for {settings.ETL_SLEEP_TIME}s")
        ev_exit.wait(settings.ETL_SLEEP_TIME)


def panic_exit(msg: str):
    logger.critical(msg)
    exit(1)


@backoff(exceptions=(ETLPipelineError,), logger_func=logger.error)
def pre_check(pipelines: list[ETLPipeline]):
    for pipeline in pipelines:
        pipeline.pre_check()


def create_fw_pipeline(state_storage: DictState) -> ETLPipeline:
    dsn = settings.PG_URI
    pg = FWExtractor(dsn, settings.PG_BATCH_SIZE)

    url = settings.ES_URI
    es = ESLoader(url, settings.ES_INDEX_MOVIES, settings.ES_BATCH_SIZE)

    return ETLPipeline(pg, ETLTransformer(), es, state_storage, "Filmworks pipeline")


def create_person_pipeline(state_storage: DictState) -> ETLPipeline:
    dsn = settings.PG_URI
    pg = PersonExtractor(dsn, settings.PG_BATCH_SIZE)

    url = settings.ES_URI
    es = ESLoader(url, settings.ES_INDEX_PERSONS, settings.ES_BATCH_SIZE, exclude={"modified", "id"})

    return ETLPipeline(pg, DummyTransformer(), es, state_storage, "Persons pipeline")


def create_genre_pipeline(state_storage: DictState) -> ETLPipeline:
    dsn = settings.PG_URI
    pg = GenreExtractor(dsn, settings.PG_BATCH_SIZE)

    url = settings.ES_URI
    es = ESLoader(url, settings.ES_INDEX_GENRES, settings.ES_BATCH_SIZE, exclude={"modified", "id"})

    return ETLPipeline(pg, DummyTransformer(), es, state_storage, "Genres pipeline")


def main():
    logger.info("Start ETL")

    if not all_ready_for_etl():
        panic_exit("Error while check system")

    storage = JsonFileStorage(STATE_FILE)
    state = DictState(storage, save_on_set=False)

    fw_pipeline = create_fw_pipeline(state)
    p_pipeline = create_person_pipeline(state)
    g_pipeline = create_genre_pipeline(state)

    pipelines = [fw_pipeline, p_pipeline, g_pipeline]

    logger.info("check conditions for ETL pipelines")
    pre_check(pipelines)

    logger.info("start pipelines")

    try:
        run(pipelines)
    except Exception as e:
        # catch ALL unexpected exceptions
        # and logging them
        logger.exception(e)
        raise

    logger.info("ETL stop")


def on_quit(sig_no: int, *args):
    logger.info(f"Interrupted by {sig_no}, shutting down")
    ev_exit.set()


if __name__ == "__main__":

    import signal

    for sig in ("TERM", "HUP", "INT"):
        signal.signal(getattr(signal, "SIG" + sig), on_quit)

    main()
