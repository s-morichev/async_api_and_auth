from http import HTTPStatus

from flask import Blueprint, jsonify, request, render_template
from flask_jwt_extended import get_jwt, jwt_required

from app.core.utils import error
from app.services import auth_service
from app.services.role_service import get_user_roles
from app.services.user_service import add_user, change_user, get_user_by_id, get_user_sessions, logout_all

default_bp = Blueprint("default", __name__)


@default_bp.get('/')
@jwt_required(optional=True)
def get_index():
    token = get_jwt()
    title = 'Sign_in'
    user_id = ''
    user_name = 'Anonymous user'
    # если токен есть - значит пользователь залогинен, возвращаем его же
    if token:
        user_id = token["sub"]
        user_name = token['name']
        user = get_user_by_id(user_id)

    return render_template("index.html", user_name=user_name, user_id=user_id)


@default_bp.get('/auth')
@jwt_required(optional=True)
def get_auth():
    token = get_jwt()
    user_id = ''
    user_name = 'Anonymous user'
    # если токен есть - значит пользователь залогинен, возвращаем его же
    if token:
        user_id = token["sub"]
        user_name = token['name']
        user = get_user_by_id(user_id)
        return render_template("index.html", user_name=user_name, user_id=user_id)

    return render_template("auth.html")
