from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.views.auth_routes import auth_bp
from app.views.role_routes import role_bp
from config import flask_config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(flask_config)
    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(role_bp, url_prefix="/roles")

    return app
