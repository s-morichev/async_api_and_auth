import time

from tests.functional.settings import settings
from redis import Redis
from redis.exceptions import RedisError

if __name__ == '__main__':
    redis_client = Redis.from_url(url=settings.REDIS_DSN)
    while True:
        try:
            if redis_client.ping():
                print('Redis connection Ok')
                break
        except RedisError:
            print('wait Redis for 1s...')
            time.sleep(1)
