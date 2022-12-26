import redis
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from .db.storage import Storage
from config import flask_config

db = SQLAlchemy()
jwt = JWTManager()
storage = Storage(flask_config.REDIS_URI)


# blacklist for access, whitelist for refresh
# jwt_redis = redis.Redis.from_url(flask_config.REDIS_URI)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    # blacklist for access
    if jwt_payload["type"] == "access":
        # access токены не проверяем на отзыв, хотя можно
        # возвращаем что не отозван
        return False

    # whitelist for refresh
    if jwt_payload["type"] == "refresh":
        jti = jwt_payload["jti"]
        user_id = jwt_payload["sub"]
        device_id = jwt_payload["device_id"]

        # если токен проходит, значит не отозван
        return not storage.check_token(user_id, device_id, jti)


def create_app():
    app = Flask(__name__)
    app.config.from_object(flask_config)
    # app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
    #
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "json"]  # так требует csrf
    # app.config["JWT_TOKEN_LOCATION"] = ["json", "cookies"] # так нет
    #app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json"] #так требует
    #app.config["JWT_TOKEN_LOCATION"] = ["headers",  "json", "cookies"] #- так не требует csrf?
    #app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
    app.config['JWT_REFRESH_COOKIE_PATH'] = '/auth/refresh'
    # app.config["JWT_COOKIE_SECURE"] = False
    db.init_app(app)
    jwt.init_app(app)

    from app.models.db_models import User

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.find_by_id(identity)

    from app.views.auth_routes import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.views.role_routes import role_bp

    app.register_blueprint(role_bp, url_prefix="/roles")

    return app
