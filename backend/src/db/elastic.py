from elasticsearch import AsyncElasticsearch

from core.database_service import ESDatabaseService

es: AsyncElasticsearch | None


# Функция понадобится при внедрении зависимостей
async def get_es_database_service() -> ESDatabaseService:
    return ESDatabaseService(elastic=es)  # noqa: F821
