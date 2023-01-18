import sys
from pathlib import Path

import pytest

src_path = Path(__file__).parent.parent / "src/"
if src_path not in sys.path:
    sys.path.insert(1, str(src_path))

from app import create_app
from app.flask_db import db
from app.services import auth_service, role_service, token_service, user_service
from config import test_config


def create_roles_and_users():
    """Cоздать роли и пользователей для тестирования. Должен быть активен app_context."""
    role_ids = []
    for role_name in ("admin", "subscriber", "user"):
        role = role_service.add_role(role_name)
        role_ids.append(role["id"])

    # example - как только что зарегистрировавшийся пользователь
    user_service.add_user("example", "example", "example")

    # example_with_roles - пользователь с добавленными ролями, в т.ч. admin
    user = user_service.add_user("example_with_roles", "example", "example")
    user_id = user["id"]
    for role_id in role_ids:
        role_service.add_user_role(user_id, role_id)

    # example_admin - пользователь c ролью только admin
    user = user_service.add_user("example_admin", "example", "example")
    user_id = user["id"]
    role_service.add_user_role(user_id, role_ids[0])


@pytest.fixture(scope="session")
def app():
    app = create_app(test_config)
    return app


@pytest.fixture
def client(app):
    with app.app_context():
        db.create_all()
        db.session.commit()

        create_roles_and_users()

        yield app.test_client()

        db.session.remove()
        db.drop_all()
        auth_service.storage.redis.flushall()


@pytest.fixture
def example_user_id(client):
    # зависит фикстуры client, должен быть активен app_context и создан пользователь
    user = role_service.database.user_by_login("example")
    return str(user.id)


@pytest.fixture
def example_with_roles_user_id(client):
    # зависит фикстуры client, должен быть активен app_context и создан пользователь
    user = role_service.database.user_by_login("example_with_roles")
    return str(user.id)


@pytest.fixture
def auth_as_admin(client):
    user = auth_service.auth("example_admin", "example")
    access_token, _ = token_service.new_tokens(user, "device_1")
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


@pytest.fixture
def invalid_uuid():
    return "not_uuid"


@pytest.fixture
def non_exist_uuid():
    return "7f32cd4a-7981-436d-bba7-78169acbbb5d"
