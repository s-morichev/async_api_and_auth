import time

from redis import Redis, ConnectionError

from functional.src.settings import settings

if __name__ == "__main__":
    redis = Redis.from_url(settings.REDIS_URI)
    while True:
        try:
            if redis.ping():
                break
        except ConnectionError:
            print("wait redis, sleep 1s")
            time.sleep(1)
