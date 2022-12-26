import redis
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from config import flask_config

db = SQLAlchemy()
jwt = JWTManager()

# blacklist for access, whitelist for refresh
jwt_redis = redis.Redis.from_url(flask_config.REDIS_URI)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    # blacklist for access
    if jwt_payload["type"] == "access":
        jti = jwt_payload["jti"]
        token_in_redis = jwt_redis.get(jti)

        return token_in_redis is not None

    # whitelist for refresh
    if jwt_payload["type"] == "refresh":
        jti = jwt_payload["jti"]
        user_id = jwt_payload["sub"]
        device_id = jwt_payload["device_id"]
        value_in_redis = jwt_redis.get(jti)

        return not value_in_redis == (user_id + "#" + device_id).encode("utf8")


def create_app():
    app = Flask(__name__)
    app.config.from_object(flask_config)
    db.init_app(app)
    jwt.init_app(app)

    from app.models.db_models import User

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.query(User).filter_by(id=identity).first()

    from app.views.auth_routes import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.views.role_routes import role_bp

    app.register_blueprint(role_bp, url_prefix="/roles")

    return app
