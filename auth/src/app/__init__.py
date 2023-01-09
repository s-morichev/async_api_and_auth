from flask import Flask

from flask_migrate import Migrate
from flask_restful import Api

from .db.storage import Storage
from .db.database import Database
from config import flask_config
from .services import token_service as token_srv
from .services import auth_service as auth_srv
from .services import role_service as role_srv

from app.views.auth_routes import auth_bp
#from app.views.role_routes import role_bp
from .flask_jwt import init_jwt
from .flask_cli import init_cli
from .flask_db import init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(flask_config)
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "json", "cookies"]  # - так не требует csrf?
    app.config['JWT_REFRESH_COOKIE_PATH'] = '/auth/refresh'
    # app.config["JWT_COOKIE_SECURE"] = False
    db = init_db(app)
    # это для  UUID->JSON
    app.config['RESTFUL_JSON'] = {'default': str}
    api = Api(app)
    # обертка редис
    storage = Storage(flask_config.REDIS_URI)
    # обертка DB
    database = Database()

    migrate = Migrate(app, db)
    init_jwt(app, storage, database)
    init_cli(app)

    # внедряем зависимости в модули
    auth_srv.database = database
    auth_srv.storage = storage
    token_srv.storage = storage
    role_srv.database = database

    app.register_blueprint(auth_bp, url_prefix="/auth")
    from app.views.role_routes import Roles, RolesList, UserRoles

    api.add_resource(RolesList, '/roles')
    api.add_resource(Roles, '/roles/<role_id>')
    api.add_resource(UserRoles, '/users/<user_id>/roles/', '/users/<user_id>/roles/<role_id>')

    #app.register_blueprint(role_bp, url_prefix="/roles")

    return app
