import json
from abc import ABC, abstractmethod
from json import JSONDecodeError
from pathlib import Path
from typing import Any


class BaseStorage(ABC):
    @abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: str):
        if not file_path:
            raise FileNotFoundError("JsonFileStorage need file path for saving state")

        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        with open(self.file_path, "w") as json_file:
            json.dump(state, json_file, default=str)

    def retrieve_state(self) -> dict:
        result = {}

        json_path = Path(self.file_path)
        if not json_path.is_file():
            return result

        with open(self.file_path, "r") as json_file:
            try:
                result = json.load(json_file)
            except JSONDecodeError:
                # if json file is broken returned empty dict
                pass

        return result


class State:
    """
    Класс для сохранения состояния
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.data = self.storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.data[key] = value
        self.storage.save_state(self.data)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        return self.data.get(key)


class DictState(State):
    """
    Dict like object which save state in BaseStorage object
    if save_on_state is set True - it will be saved every changing
    otherwise only when save_state() calling
    """

    def __init__(self, storage: BaseStorage, save_on_set=True):
        self.save_on_state = save_on_set
        super().__init__(storage)

    def set_state(self, key: str, value: Any) -> None:
        self.data[key] = value
        if self.save_on_state:
            self.storage.save_state(self.data)

    def save_state(self):
        self.storage.save_state(self.data)

    def __getitem__(self, item):
        return super().get_state(item)

    def __setitem__(self, key, value):
        self.set_state(key, value)

    def get(self, item):
        return self.__getitem__(item)
