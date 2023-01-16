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


@pytest.fixture
def app():
    app = create_app(test_config)
    # импорт после создания и внедрения database
    from app.services.auth_service import database

    with app.app_context():
        db.create_all()
        db.session.commit()

        for role_name in ("admin", "subscriber", "user"):
            role_service.add_role(role_name)

        user_service.add_user("example", "example", "example")

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
