from typing import Any, Generic, TypeVar

from pydantic.generics import BaseModel, GenericModel

ModelT = TypeVar("ModelT")


class ServiceResult(BaseModel):
    """класс для возврата данных со служебной информацией"""

    total: int = 0
    page_num: int = 0
    page_size: int = 0
    cached: int = 0  # данные из кэша или нет


class ServiceSingeResult(ServiceResult, GenericModel, Generic[ModelT]):
    result: ModelT

    @classmethod
    def __concrete_name__(cls: type[Any], params: tuple[type[Any], ...]) -> str:
        return f"{params[0].__name__.title()}ServiceSingeResult"


class ServiceListResult(ServiceResult, GenericModel, Generic[ModelT]):
    result: list[ModelT]

    @classmethod
    def __concrete_name__(cls: type[Any], params: tuple[type[Any], ...]) -> str:
        return f"{params[0].__name__.title()}ServiceListResult"
