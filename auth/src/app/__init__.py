from flasgger import Swagger
from flask import Flask, request
from flask_migrate import Migrate

from app.core.exceptions import AuthServiceError, http_error_handler
from app.db.database import Actions, Roles, Users
from app.db.storage import Storage
from app.flask_cli import init_cli
from app.flask_db import init_db
from app.flask_jwt import init_jwt
from app.flask_tracing import init_tracer
from app.services import auth_service as auth_srv
from app.services import role_service as role_srv
from app.services import token_service as token_srv
from app.services import user_service as user_srv
from app.views import auth_bp


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "json", "cookies"]  # - так не требует csrf?
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/auth/v1/refresh"
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

    app.register_error_handler(AuthServiceError, http_error_handler)

    @app.before_request
    def before_request():
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            raise RuntimeError('request id is required')

    init_tracer(app)

    return app
