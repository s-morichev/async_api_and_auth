from redis.asyncio import Redis

from core.cache_service import RedisCacheService

redis: Redis | None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return RedisCacheService(redis=redis)  # noqa: F821
