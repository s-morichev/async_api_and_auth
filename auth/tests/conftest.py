import sys
from pathlib import Path

import pytest

src_path = Path(__file__).parent.parent / "src/"
if src_path not in sys.path:
    sys.path.insert(1, str(src_path))

from app import create_app
from app.flask_db import db
from app.services import auth_service, role_service, user_service
from config import test_config


@pytest.fixture(scope="session")
def app():
    app = create_app(test_config)
    # импорт после создания и внедрения database
    from app.services.auth_service import database

    return app


@pytest.fixture
def client(app):
    with app.app_context():
        db.create_all()
        db.session.commit()

        # создаем роли и двоих пользователей для тестирования
        # example - как только что зарегистрировавшийся пользователь
        # example_with_roles - пользователь с добавленными ролями
        role_ids = []
        for role_name in ("admin", "subscriber", "user"):
            role = role_service.add_role(role_name)
            role_ids.append(role["id"])

        user_service.add_user("example", "example", "example")
        user = user_service.add_user("example_with_roles", "example", "example")
        user_id = user["id"]
        for role_id in role_ids:
            role_service.add_user_role(user_id, role_id)

        yield app.test_client()

        db.session.remove()
        db.drop_all()
        auth_service.storage.redis.flushall()
