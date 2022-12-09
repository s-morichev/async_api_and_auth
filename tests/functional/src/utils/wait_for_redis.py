import time

from redis import Redis

from settings import settings

if __name__ == "__main__":
    redis = Redis.from_url(settings.REDIS_URI)
    while True:
        if redis.ping():
            break
        print("wait redis, sleep 1s")
        time.sleep(1)
