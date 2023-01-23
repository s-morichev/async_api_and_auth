from flask import Blueprint

from .me_routes import me_bp
from .auth_routes import auth_bp
from .role_routes import role_bp
from .user_routes import user_bp

auth_v1 = Blueprint('auth_v1', __name__, url_prefix='/v1')

auth_v1.register_blueprint(me_bp)
auth_v1.register_blueprint(auth_bp)
auth_v1.register_blueprint(role_bp)
auth_v1.register_blueprint(user_bp)
