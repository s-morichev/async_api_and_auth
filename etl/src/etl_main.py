from threading import Event
from datetime import datetime

import etl_logger
from es_loader import ESLoader
from etl_pipeline import ETLPipeline, ETLPipelineError
from etl_transformer import ETLTransformer
from etl_utils import es_create_index_if_not_exist
from pg_extractor import PGExtractor
from settings import settings, STATE_FILE
from storage import JsonFileStorage

logger = etl_logger.get_logger('ETL')
ev_exit = Event()


def all_ready_for_etl() -> bool:
    """
    создаем индекс в ES если он отсутствует
    Но в проде он же будет создан до запуска?
    """
    return es_create_index_if_not_exist()


def run(pipeline: ETLPipeline):
    while not ev_exit.is_set():
        start_time = datetime.now()
        pipeline.execute()
        end_time = datetime.now()
        logger.info('-------------------------------------------------')
        logger.info(f'ETL executed. Time elapsed:{end_time - start_time}')
        logger.info(f'record loaded:{pipeline.state["data_count"]}')
        logger.info(f'wait for {settings.ETL_SLEEP_TIME}s')
        ev_exit.wait(settings.ETL_SLEEP_TIME)


def panic_exit(msg: str):
    logger.critical(msg)
    exit(1)


def main():
    logger.info('Start ETL')

    if not all_ready_for_etl():
        panic_exit('Error while check system')

    storage = JsonFileStorage(STATE_FILE)

    dsn = settings.PG_URI
    pg = PGExtractor(dsn, settings.BATCH_SIZE)

    url = settings.ES_URI
    es = ESLoader(url, settings.ES_INDEX_MOVIES)

    pipeline = ETLPipeline(pg, ETLTransformer(), es, storage)

    logger.info('check conditions for ETL')

    # проверка на условия для запуска ETL
    # если требуется - можно сделать ожидание
    # а не прекращать работу
    try:
        pipeline.pre_check()
    except ETLPipelineError as e:
        if settings.DEBUG:
            logger.exception(e)
        else:
            logger.critical(e)

        panic_exit('There are no working conditions. exit ETL')

    logger.info('execute ETL')

    try:
        run(pipeline)
    except Exception as e:
        # catch ALL unexpected exceptions
        # and logging them
        logger.exception(e)
        raise

    logger.info('ETL stop')


def on_quit(sig_no: int, *args):
    logger.info(f"Interrupted by {sig_no}, shutting down")
    ev_exit.set()


if __name__ == '__main__':

    import signal

    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(getattr(signal, 'SIG' + sig), on_quit)

    main()
