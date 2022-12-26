import hashlib
from http import HTTPStatus

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import current_user, get_jwt, jwt_required, set_access_cookies, unset_jwt_cookies
from flask_jwt_extended import set_refresh_cookies, get_csrf_token, decode_token

import app
from app.services import auth_service

auth_bp = Blueprint("auth", __name__)


def msg(message: str) -> Response:
    """функция для унификации сообщений"""
    return jsonify({'msg': message})


@auth_bp.post("/register")
def register():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    # если имя не указано, используем e-mail
    name = request.json.get("password", email)
    if email is None or password is None:
        return msg("No email or password"), HTTPStatus.BAD_REQUEST

    auth_service.register_user(email, password, name)
    return msg("Registered")


@auth_bp.post("/login")
@jwt_required(optional=True)
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user_agent = request.headers.get("User-Agent")
    access_jti = get_jwt().get("jti", None)

    if email is None or password is None:
        return msg("No email or password"), HTTPStatus.BAD_REQUEST

    try:
        access, refresh = auth_service.login(email, password, user_agent, access_jti)
    except auth_service.CredentialError:
        return msg("Invalid email or password"), HTTPStatus.UNAUTHORIZED

    # TODO use httponly cookie, add csrf protection
    print(decode_token(access))
    print(decode_token(refresh))
    print(app.flask_config)
    access_csrf_token = get_csrf_token(access)
    refresh_csrf_token = get_csrf_token(refresh)
    response = jsonify(access_token=access, refresh_token=refresh,
                       access_csrf=access_csrf_token, refresh_csrf=refresh_csrf_token)
    set_refresh_cookies(response, refresh)
    return response


# пример из flask_jwt_extended
@auth_bp.get("/me")
@jwt_required()
def me():
    # We can now access our sqlalchemy User object via `current_user`.
    claims = get_jwt()
    return jsonify(
        id=current_user.id, email=current_user.email, username=current_user.username, role_claims=claims["roles"]
    )


@auth_bp.post("/logout")
@jwt_required()
def logout():

    payload = get_jwt()
    auth_service.logout(payload)
    response = msg("Logged out")
    unset_jwt_cookies(response)
    return response


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_agent = request.headers.get("User-Agent")
    device_id = hashlib.sha256(user_agent.encode("utf8")).hexdigest()

    payload = get_jwt()
    if device_id != payload.get("device_id"):
        return msg("Token invalidated"), HTTPStatus.UNAUTHORIZED

    access, refresh = auth_service.refresh(payload)
    return jsonify(access_token=access, refresh_token=refresh)


@jwt_required(fresh=True)
def change_email():
    pass


@jwt_required(fresh=True)
def change_password():
    pass
