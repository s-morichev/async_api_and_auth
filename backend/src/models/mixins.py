from uuid import UUID

import orjson
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    """Сериализует объект в строку JSON."""
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class BaseMixin(BaseModel):
    """Базовый класс для ресурсов."""

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        # позволит использовать в названии полей псевдонимы
        allow_population_by_field_name = True


class IdMixin(BaseModel):
    uuid: UUID = Field(alias="id")
