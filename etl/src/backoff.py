from functools import wraps
from time import sleep


def backoff(
    exceptions, start_sleep_time: float = 0.1, factor: float = 2, border_sleep_time: float = 30, logger_func=None
):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param logger_func: Функция вида func(msg:str)
    :param exceptions: список прерываний для перехвата
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            count = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    count += 1
                    if logger_func:
                        logger_func(f"Error ({count}):[{e}]")
                        logger_func(f" Wait for {sleep_time}s for repeat")

                    sleep(sleep_time)
                    # increase sleep time
                    if sleep_time <= border_sleep_time / factor:
                        sleep_time *= factor
                    else:
                        sleep_time = border_sleep_time

        return inner

    return func_wrapper


def backoff_gen(
    exceptions, start_sleep_time: float = 0.1, factor: float = 2, border_sleep_time: float = 30, logger_func=None
):
    """
    Декоратор для генератора
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param logger_func: Функция вида func(msg:str)
    :param exceptions: список прерываний для перехвата
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            count = 0
            while True:
                try:
                    ret = yield from func(*args, **kwargs)
                    return ret
                except exceptions as e:
                    count += 1
                    if logger_func:
                        logger_func(f"Error ({count}):[{e}]")
                        logger_func(f" Wait for {sleep_time}s for repeat")

                    sleep(sleep_time)
                    # increase sleep time
                    if sleep_time <= border_sleep_time / factor:
                        sleep_time *= factor
                    else:
                        sleep_time = border_sleep_time

        return inner

    return func_wrapper
