from http import HTTPStatus

import pytest


def test_get_basic_roles(client):
    response = client.get("/auth/roles")

    assert response.status_code == HTTPStatus.OK
    for role in response.json:
        assert "id" in role
        assert "name" in role
        assert len(role) == 2

    assert len(response.json) == 3
    assert set(role["name"] for role in response.json) == {"admin", "subscriber", "user"}


def test_create_role(client):
    response = client.post("/auth/roles", json={"name": "test"})

    assert response.status_code == HTTPStatus.CREATED
    assert response.json["name"] == "test"


@pytest.mark.parametrize(
    "query, status_code",
    [
        ({"name": "admin"}, HTTPStatus.CONFLICT),
        ({"invalid key": "test"}, HTTPStatus.BAD_REQUEST),
        ({"name": "test", "excess_key": "value"}, HTTPStatus.CREATED),
    ]
)
def test_create_role_errors(query, status_code, client):
    response = client.post(
        '/auth/roles',
        json=query
    )

    assert response.status_code == status_code
