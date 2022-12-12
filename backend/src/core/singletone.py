"""
Singletone class for Singletone pattern
usage: class SingletonClass(metaclass=Singleton):
"""


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            print(f"singletone create {cls}")
        return cls._instances[cls]
