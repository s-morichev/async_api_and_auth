import pytest
from http import HTTPStatus


def test_login(client):
    response = client.post(
        '/auth/login',
        json={
            "email": "test",
            "password":"test"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json
    assert "refresh_token" in response.json
    assert "refresh_token_cookie" in response.headers["Set-Cookie"]
    assert "HttpOnly" in response.headers["Set-Cookie"]
    assert "Path=/auth/refresh" in response.headers["Set-Cookie"]


@pytest.mark.parametrize(
    "query, status_code",
    [
        ({"email": "not email", "password": "test"}, HTTPStatus.UNAUTHORIZED),
        ({"email": "test", "password": "invalid"}, HTTPStatus.UNAUTHORIZED),
        ({"invalid_key": "test", "password": "test"}, HTTPStatus.BAD_REQUEST),
        ({"email": "test"}, HTTPStatus.BAD_REQUEST),
        ({"password": "test"}, HTTPStatus.BAD_REQUEST),
        ({"invalid_key": "test", "password": "test", "excess_key": "value"}, HTTPStatus.BAD_REQUEST),
    ]
)
def test_login_errors(query, status_code, client):
    response = client.post('/auth/login', json=query)
    assert response.status_code == status_code
