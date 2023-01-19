from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from app.services import auth_service
from app.services.role_service import get_user_roles
from app.services.user_service import RegisterError, add_user, change_user, get_user_by_id, get_user_sessions
from app.core.utils import error

me_bp = Blueprint("me", __name__)


@me_bp.get("/")
@jwt_required()
def get_info():
    """get user data"""
    token = get_jwt()
    user_id = token["sub"]
    user = get_user_by_id(user_id)
    return jsonify(user)


@me_bp.post("/")
@jwt_required(optional=True)
def new_user():
    """new user create or return exist user if logined"""
    user = None
    token = get_jwt()
    # если токен есть - значит пользователь залогинен, возвращаем его же
    if token:
        user_id = token["sub"]
        user = get_user_by_id(user_id)
        return jsonify(user), HTTPStatus.IM_A_TEAPOT

    email = request.json.get("email", None)
    password = request.json.get("password", None)
    name = request.json.get("name", None)
    if not (email and password):
        error("email and password info required", HTTPStatus.BAD_REQUEST)

    try:
        user = add_user(email, password, name)
    except RegisterError as err:
        error(str(err), HTTPStatus.CONFLICT)

    return jsonify(user), HTTPStatus.CREATED


@me_bp.patch("/")
@jwt_required()
def change_info():
    token = get_jwt()
    user_id = token["sub"]

    password = request.json.get("password", None)
    name = request.json.get("name", None)
    user = change_user(user_id, None, password, name)

    return jsonify(user)


@me_bp.get("/roles")
@jwt_required()
def get_roles():
    token = get_jwt()
    user_id = token["sub"]

    roles = get_user_roles(user_id)
    return jsonify(roles)


@me_bp.get("/history")
@jwt_required()
def get_history():
    token = get_jwt()
    user_id = token["sub"]

    history = auth_service.get_user_history(user_id)
    return jsonify(history)


@me_bp.get("/sessions")
@jwt_required()
def get_sessions():
    token = get_jwt()
    user_id = token["sub"]

    sessions = get_user_sessions(user_id)
    return jsonify(sessions)
