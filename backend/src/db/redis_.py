from core.cache_service import RedisCacheService
from redis.asyncio import Redis

redis: Redis | None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return RedisCacheService(redis=redis)  # noqa: F821
