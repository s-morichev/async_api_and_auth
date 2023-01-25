from flasgger import Swagger
from flask import Flask
from flask_migrate import Migrate

from app.core.exceptions import AuthServiceError, http_error_handler
from app.db.database import Actions, Roles, Users
from app.db.storage import Storage
from app.flask_cli import init_cli
from app.flask_db import init_db
from app.flask_jwt import init_jwt
from app.services import auth_service as auth_srv
from app.services import role_service as role_srv
from app.services import token_service as token_srv
from app.services import user_service as user_srv
from app.views import auth_bp
from app.views.default_routes import default_bp



def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "json", "cookies"]  # - так не требует csrf?
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/auth/v1/refresh"
    app.config['OAUTH_CREDENTIALS'] = {
        'yandex': {
            'id': '1e4171dd3d1647249c5e2a0d78c5eac2',
            'secret': '7d60d4de74084c1ab1f07615931fe8bb'
        },
        'vk': {
            'id': '51534244',
            'secret': 'zUQ47SJ0d2uP85SRXSHE'
        }
    }

    db = init_db(app)
    # это для  UUID->JSON
    app.config["RESTFUL_JSON"] = {"default": str}
    # обертка редис
    storage = Storage(config.REDIS_URI)
    # обертка DB
    users = Users()
    roles = Roles()
    actions = Actions()

    Swagger(app, template_file=config.OPENAPI_YAML)
    Migrate(app, db)
    init_cli(app)

    # внедряем зависимости в модули
    auth_srv.users = users
    auth_srv.actions = actions
    auth_srv.storage = storage

    token_srv.users = users
    token_srv.storage = storage

    role_srv.users = users
    role_srv.roles = roles

    user_srv.users = users

    init_jwt(app, token_srv, users)

    app.register_blueprint(auth_bp)
    app.register_blueprint(default_bp)

    app.register_error_handler(AuthServiceError, http_error_handler)
    return app
