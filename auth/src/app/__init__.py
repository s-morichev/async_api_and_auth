from flasgger import Swagger
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api

from app.views.auth_routes import auth_bp
from app.views.me_routes import me_bp
from app.views.role_routes import role_bp
from app.views.user_routes import user_bp

from app.db.database import Database
from app.db.storage import Storage
from app.core.exceptions import AuthServiceError, http_error_handler
from app.flask_cli import init_cli
from app.flask_db import init_db
from app.flask_jwt import init_jwt
from app.services import auth_service as auth_srv
from app.services import role_service as role_srv
from app.services import token_service as token_srv
from app.services import user_service as user_srv


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "json", "cookies"]  # - так не требует csrf?
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/auth/refresh"
    db = init_db(app)
    # это для  UUID->JSON
    app.config["RESTFUL_JSON"] = {"default": str}
    api = Api(app)
    # обертка редис
    storage = Storage(config.REDIS_URI)
    # обертка DB
    database = Database()

    swagger = Swagger(app, template_file=config.OPENAPI_YAML)
    migrate = Migrate(app, db)
    init_cli(app)

    # внедряем зависимости в модули
    auth_srv.database = database
    auth_srv.storage = storage
    token_srv.storage = storage
    token_srv.database = database
    role_srv.database = database
    user_srv.database = database

    init_jwt(app, token_srv, database)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(me_bp, url_prefix="/auth/users/me")
    app.register_blueprint(role_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/auth")

    app.register_error_handler(AuthServiceError, http_error_handler)
    return app
