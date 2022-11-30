from models.base_dto import BaseDTO


class ServiceResult(BaseDTO):
    """класс для возврата данных со служебной информацией"""

    total: int = 0
    page_num: int = 0
    page_size: int = 0
    cached: int = 0  # данные из кэша или нет
    result: BaseDTO | list[BaseDTO]  # Result for query
