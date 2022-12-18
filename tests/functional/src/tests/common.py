import json
from typing import Type

from ..settings import BASE_DIR
from ..utils.core_model import CoreModel


# ------------------------------------------------------------------------------ #
def check_single_response(status, body, expected_result):
    """
    для ответа из одной позиции. проверяем результат на соответствие
    'status' - проверяет статус ответа
     key - остальные ключи проверяются на [key]
     '!key' - пропускается (можно сделать отдельную обработку)

    """
    for key in expected_result:
        if key[0] == "!":
            continue

        match key:
            case "status":
                assert status == expected_result["status"]

            case _:
                assert (body[key]) == expected_result[key]


def check_multi_response(status, body, expected_result):
    """
    для ответа из многих позиций. проверяем результат на соответствие
    'status' - проверяет статус ответа
    'total' - количество записей всего (поле total в ответе)
    'length' - количество вернувшихся записей в result
     key - остальные ключи проверяются на result[0..len][key] (то есть в любой позиции)
         - 'num#key' - result[num][key] - в позиции num
         - '!key' - пропускается (можно сделать отдельную обработку)
    """

    for key in expected_result:
        if key[0] == "!":
            continue

        match key:
            case "status":
                assert status == expected_result["status"]

            case "total":
                assert body["total"] == expected_result["total"]

            case "length":
                assert len(body["result"]) == expected_result["length"]

            case _:
                expected_value = expected_result[key]
                # key like '123#title', result[123][title]==expected value
                if "#" in key:
                    num_key = key.split("#")
                    num = int(num_key[0] or "0")
                    key = num_key[1]
                    assert body["result"][num][key] == expected_value
                else:
                    is_key_test = False
                    for row in body["result"]:
                        if key in row and row[key] == expected_value:
                            is_key_test = True
                            break
                    assert is_key_test, f"{key}:{expected_value} Not found in result"


# ------------------------------------------------------------------------------ #
def args(data: list[tuple]):
    return [row[:2] for row in data]


def ids(data: list[tuple]):
    return [row[2] for row in data]


# ------------------------------------------------------------------------------ #
def load_from_json(filename: str, Model: Type[CoreModel]):
    """загружает из файла json и возвращает список из моделей Model"""

    testdata_dir = BASE_DIR / "testdata/"

    with open(testdata_dir / filename, "r") as file:
        json_list = json.load(file)

    result = [Model(**row) for row in json_list]

    return result


# ------------------------------------------------------------------------------ #
def get_pagination_test_data(
    total_row_count: int, default_page_size: int = 50, max_page_size: int = 200, mixin: dict | None = None
):
    """
    Готовим тестовый набор для проверки пагинации
    :param total_row_count - количество записей всего в наборе
    :param default_page_size - размер страницы если ее не указать
    :param max_page_size - размер максимально допустимой страницы
    :param mixin - подмешивает в запрос эти данные
    """
    # количество записей на странице при странице по умолчанию
    # размер страницы 1
    page_1 = min(total_row_count, default_page_size)
    # размер страницы 2
    page_2 = max(0, min(total_row_count - default_page_size, default_page_size))
    testdata = [
        ({"page[number]": -1, "page[size]": 3}, {"status": 422}, "page_num=-1"),
        ({"page[number]": -1}, {"status": 422}, "page_num=-1 without page_size"),
        ({"page[number]": 0, "page[size]": 3}, {"status": 422}, "page_num=0"),
        ({"page[number]": 0}, {"status": 422}, "page_num=0 without page_size"),
        ({"page[number]": 'aaa'}, {"status": 422}, "page_num=string"),
        ({"page[size]": 'bbb'}, {"status": 422}, "page_size=string"),
        ({"page[number]": 'qwerty', "page[size]": 'qwerty'}, {"status": 422}, "page_size and page_num=string"),
        ({"page[number]": 1000000, "page[size]": default_page_size}, {"status": 400}, "big page_size*page_num"),
        ({"page[number]": 2, "page[size]": max_page_size + 1}, {"status": 422}, "page_size>max_page_size"),
    ]
    # эти тесты применимы если не пустой список
    if total_row_count > 0:
        testdata += [
            ({"page[number]": 1, "page[size]": 50}, {"status": 200, "total": total_row_count}, "default pagination"),
            ({}, {"status": 200, "length": page_1, "total": total_row_count}, "no pages send"),
            ({"page[number]": 1}, {"status": 200, "length": page_1}, "only page number=1"),
            ({"page[number]": 2}, {"status": 200, "length": page_2}, "page number=2"),
            (
                {"page[number]": 1, "page[size]": page_1 - 1},
                {"status": 200, "length": page_1 - 1},
                "limit page full_page",
            ),
            ({"page[number]": 1, "page[size]": 1}, {"status": 200, "length": 1}, "limit page=1"),
            (
                {"page[number]": 2, "page[size]": page_1 - 1},
                {"status": 200, "length": 1},
                "page=2, page_size must be 1",
            ),
            ({"page[size]": 1}, {"status": 200, "length": 1}, "only page size=1"),
        ]

    if mixin:
        for row in testdata:
            row[0].update(mixin)
        # testdata = [(row[0] | mixin, row[1:]) for row in testdata]

    return testdata


# ------------------------------------------------------------------------------ #
