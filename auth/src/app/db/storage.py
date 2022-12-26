import redis


class Storage:
    redis: redis.Redis

    def __init__(self, redis_uri):
        self.redis = redis.from_url(redis_uri)

    @staticmethod
    def _key(user_id, device_id):
        return f'{user_id}#{device_id}'

    def set_token(self, user_id, device_id, token, expires):
        key = self._key(user_id, device_id)
        self.redis.set(name=key, value=token, ex=expires)

    def check_token(self, user_id, device_id, token):
        key = self._key(user_id, device_id)
        value = self.redis.get(key).decode('utf-8')
        result = value and (value == token)
        return result

    def remove_key(self, user_id, device_id):
        key = self._key(user_id, device_id)
        self.redis.delete(key)