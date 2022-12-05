import logging

from core.settings import LOG_FILE, settings

if settings.DEBUG:
    _log_format = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s -- (%(filename)s).%(funcName)s(%(lineno)d)"
    FILE_LOG_LEVEL = logging.DEBUG
    STREAM_LOG_LEVEL = logging.DEBUG
else:
    FILE_LOG_LEVEL = logging.WARNING
    STREAM_LOG_LEVEL = logging.INFO
    _log_format = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"


def _get_file_handler() -> logging.FileHandler:
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(FILE_LOG_LEVEL)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def _get_stream_handler() -> logging.StreamHandler:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(STREAM_LOG_LEVEL)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name: str) -> logging.Logger:
    """
    return loger object with stream and file output
    file for loging set by LOG_FILE setting in module app_settings

    usual usage:
            logger = app_logger.get_logger(__name__)
            logger.info('bla bla bla')
    """
    logger = logging.getLogger(name)
    logger.setLevel(STREAM_LOG_LEVEL)
    logger.addHandler(_get_file_handler())
    logger.addHandler(_get_stream_handler())
    return logger
