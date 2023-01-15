import redis
from abc import ABC, abstractmethod


# YAGNI
class AbstractStorage(ABC):
    @abstractmethod
    def set_token(self, user_id, device_id, token_id, expires):
        """ устанавливаем токен как валидный"""

    @abstractmethod
    def check_token(self, user_id, device_id, token_id):
        """проверяем токен на валидность"""

    @abstractmethod
    def remove_session(self, user_id, device_id):
        """ удаляем сессию пользователя"""


class Storage(AbstractStorage):
    """Быстрое хранилище для ключей - типа Редис"""
    redis: redis.Redis

    def __init__(self, redis_uri):
        self.redis = redis.from_url(redis_uri)

    @staticmethod
    def _key(user_id, device_id):
        return f'{user_id}#{device_id}'

    def set_token(self, user_id, device_id, token_id, expires):
        key = self._key(user_id, device_id)
        self.redis.set(name=key, value=token_id, exat=expires)

    def check_token(self, user_id, device_id, token_id):
        key = self._key(user_id, device_id)
        value = self.redis.get(key)
        result = value and (value.decode('utf-8') == token_id)
        return result

    def remove_session(self, user_id, device_id):
        key = self._key(user_id, device_id)
        self.redis.delete(key)
