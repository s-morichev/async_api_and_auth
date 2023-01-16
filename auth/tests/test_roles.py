from http import HTTPStatus

import pytest

from app.services import role_service


@pytest.fixture
def user_role_id():
    roles = role_service.get_all_roles()
    role_id = [role["id"] for role in roles if role["name"] == "user"][0]
    return role_id


@pytest.fixture
def invalid_uuid():
    return "not_uuid"


@pytest.fixture
def non_exist_uuid():
    return "7f32cd4a-7981-436d-bba7-78169acbbb5d"

def test_get_all_roles(client):
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
    assert response.json.get("name") == "test"

    role_id = response.json.get("id")
    response = client.get(f"/auth/roles/{role_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json.get("name") == "test"


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


def test_get_role(client, user_role_id):
    response = client.get(f"/auth/roles/{user_role_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json.get("name") == "user"


@pytest.mark.parametrize(
    "role_id, status_code",
    [
        ("not_uuid", HTTPStatus.UNPROCESSABLE_ENTITY),
        ("7f32cd4a-7981-436d-bba7-78169acbbb5d", HTTPStatus.NOT_FOUND),
    ]
)
def test_get_role_errors(role_id, status_code, client):
    response = client.get(f"/auth/roles/{role_id}")
    assert response.status_code == status_code


def test_update_role(client, user_role_id):
    response = client.put(f"/auth/roles/{user_role_id}", json={"name":"new name"})
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get(f"/auth/roles/{user_role_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json.get("name") == "new name"


@pytest.mark.parametrize(
    "role_id_fixture, query, status_code",
    [
        ("user_role_id", {"invalid key": "new_name"}, HTTPStatus.BAD_REQUEST),
        ("user_role_id", {"name": "new_name", "excess_key": "value"}, HTTPStatus.NO_CONTENT),
        ("invalid_uuid", {"name": "new_name"}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ("non_exist_uuid", {"name": "new_name"}, HTTPStatus.NOT_FOUND),
    ]
)
def test_update_role_errors(role_id_fixture, query, status_code, client, request):
    role_id = request.getfixturevalue(role_id_fixture)
    response = client.put(f"/auth/roles/{role_id}", json=query)
    assert response.status_code == status_code


def test_delete_role(client, user_role_id):
    response = client.delete(f"/auth/roles/{user_role_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get(f"/auth/roles/{user_role_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    "role_id, status_code",
    [
        ("not_uuid", HTTPStatus.UNPROCESSABLE_ENTITY),
        ("7f32cd4a-7981-436d-bba7-78169acbbb5d", HTTPStatus.NOT_FOUND),
    ]
)
def test_delete_role_errors(role_id, status_code, client):
    response = client.delete(f"/auth/roles/{role_id}")
    assert response.status_code == status_code
