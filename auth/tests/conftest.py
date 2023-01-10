import sys
from pathlib import Path
import pytest

src_path = Path(__file__).parent.parent / "src/"
if src_path not in sys.path:
    sys.path.insert(1, str(src_path))

from app import create_app
from app.flask_db import db
from app.models.db_models import Role

from config import test_config


@pytest.fixture
def app():
    app = create_app(test_config)
    # импорт после создания и внедрения database
    from app.services.auth_service import database

    with app.app_context():
        db.create_all()
        for role_name in ("admin", "subscriber", "user"):
            db.session.add(Role(name=role_name))
        db.session.commit()

        database.add_user("test", "test", "test")

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
