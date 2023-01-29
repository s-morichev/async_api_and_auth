from http import HTTPStatus

import pytest
import pytest_asyncio

from ..settings import settings
from ..utils.dto_models import ElasticFilm
from ..utils.tokens import generate_access_token
from .common import load_from_json

pytestmark = pytest.mark.asyncio

# ------------------------------------------------------------------------------ #
total_rows = 20


@pytest_asyncio.fixture(scope="module", autouse=True)
async def prepare_data(es_write_data, flush_data):
    films = load_from_json("films2.json", ElasticFilm)
    assert len(films) == total_rows
    es_index = settings.ES_MOVIES_INDEX

    await es_write_data(index=es_index, documents=films, id_key="id", exclude={})


async def test_no_auth_header(make_get_request):
    url = "/api/v1/view/edbb87fd-bfdb-458d-852d-61d6f3f67551"
    body, header, status = await make_get_request(url)

    assert status == HTTPStatus.FORBIDDEN


async def test_valid_access_token(make_get_request):
    url = "/api/v1/view/edbb87fd-bfdb-458d-852d-61d6f3f67551"
    token = generate_access_token(1000, ["user"])
    body, header, status = await make_get_request(url, access_token=token)

    assert status == HTTPStatus.OK


async def test_root_access(make_get_request):
    url = "/api/v1/view/edbb87fd-bfdb-458d-852d-61d6f3f67551"
    token = generate_access_token(1000, ["ROOT"])
    body, header, status = await make_get_request(url, access_token=token)

    assert status == HTTPStatus.OK


@pytest.mark.parametrize(
    "expire, roles, jwt_key, status",
    [
        (-10, ["user"], None, HTTPStatus.UNAUTHORIZED),
        (1000, ["non_exist_role"], None, HTTPStatus.FORBIDDEN),
        (1000, ["user"], "invalid key", HTTPStatus.UNAUTHORIZED),
        (1000, ["ROOT"], "invalid key", HTTPStatus.UNAUTHORIZED),
    ],
)
async def test_expired_access_token(expire, roles, jwt_key, status, make_get_request):
    url = "/api/v1/view/edbb87fd-bfdb-458d-852d-61d6f3f67551"
    token = generate_access_token(expire, roles, jwt_key)
    body, header, resp_status = await make_get_request(url, access_token=token)

    assert resp_status == status
