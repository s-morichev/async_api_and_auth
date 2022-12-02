import hashlib

import orjson
from core.constants import DEFAULT_PAGE_SIZE, KEY_PAGE_NUM, KEY_PAGE_SIZE, MAX_PAGE_SIZE


def hash_dict(pretty_key: str, key_dict: dict):
    """return hash for dict with pretty key at first
    for example:
    GET_PERSON:4acc71e0547112eb432f0a36fb1924c4a738cb49
    """
    s_key = orjson.dumps(key_dict, option=orjson.OPT_SORT_KEYS)
    return f"{pretty_key}:{hashlib.sha1(s_key).hexdigest()}"


def restrict_pages(query_dict: dict | None) -> dict:
    """создает пагинауию если ее нет и ограничивает до MAX_PAGE_SIZE на странице"""
    if not query_dict:
        return {KEY_PAGE_NUM: 1, KEY_PAGE_SIZE: DEFAULT_PAGE_SIZE}
    else:
        # устанавливаем размер страницы, если нет
        query_dict[KEY_PAGE_SIZE] = min(MAX_PAGE_SIZE, query_dict.get(KEY_PAGE_SIZE) or DEFAULT_PAGE_SIZE)

        # устанавливаем страницу в 1, если нет
        query_dict[KEY_PAGE_NUM] = query_dict.setdefault(KEY_PAGE_NUM, 1)

        return query_dict


class classproperty(object):
    """classproperty decorator"""

    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)
