from http import HTTPStatus

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import current_user, get_jwt, jwt_required, unset_jwt_cookies
from flask_jwt_extended import set_refresh_cookies

from app.services import auth_service
from app.services import token_service

auth_bp = Blueprint("auth", __name__)


# ------------------------------------------------------------------------------ #
def msg(message: str) -> Response:
    """функция для унификации сообщений"""
    return jsonify({'msg': message})


@auth_bp.post("/register")
def register():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    # если имя не указано, используем e-mail
    name = request.json.get("name", email)

    if email is None or password is None:
        return msg("No email or password"), HTTPStatus.BAD_REQUEST
    try:
        auth_service.register_user(email, password, name)
    except auth_service.RegisterError as err:
        return msg(str(err)), HTTPStatus.CONFLICT

    return msg("Registered")


@auth_bp.post("/login")
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user_agent = request.headers.get("User-Agent")
    remote_ip = request.remote_addr

    if email is None or password is None:
        return msg("No email or password"), HTTPStatus.BAD_REQUEST

    try:
        user = auth_service.login(email, password, user_agent, remote_ip)

    except auth_service.CredentialError:
        return msg("Invalid email or password"), HTTPStatus.UNAUTHORIZED

    access_token, refresh_token = token_service.new_tokens(user, user_agent)

    # TODO csrf is needed????
    # access_csrf_token = get_csrf_token(access_token)
    # refresh_csrf_token = get_csrf_token(refresh_token)
    # response = jsonify(access_token=access_token, refresh_token=refresh_token,
    #                    access_csrf=access_csrf_token, refresh_csrf=refresh_csrf_token)

    response = jsonify(access_token=access_token, refresh_token=refresh_token)
    set_refresh_cookies(response, refresh_token)

    return response


# пример из flask_jwt_extended
# @auth_bp.get("/me")
@auth_bp.route('/me', methods=["GET", "POST"])
@jwt_required()
def me():
    # We can now access our sqlalchemy User object via `current_user`.
    claims = get_jwt()
    return jsonify(current_user.dict())
    # return jsonify(
    #     id=current_user.id, email=current_user.email, username=current_user.username, role_claims=claims["roles"]
    # )


@auth_bp.post("/logout")
@jwt_required()
def logout():
    token = get_jwt()
    user_id = token['sub']
    device_id = token['device_id']

    auth_service.logout(user_id, device_id)
    token_service.logout(user_id, device_id)

    response = msg("Logged out")
    unset_jwt_cookies(response)

    return response


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    payload = get_jwt()

    user_agent = request.headers.get("User-Agent")
    if not token_service.is_valid_device(user_agent, payload):
        return msg("Token invalidated"), HTTPStatus.UNAUTHORIZED

    user_id = payload['sub']
    device_id = payload['device_id']

    auth_service.refresh(user_id, device_id)
    access_token, refresh_token = token_service.refresh_tokens(payload)

    return jsonify(access_token=access_token, refresh_token=refresh_token)


@jwt_required(fresh=True)
def change_email():
    pass


@jwt_required(fresh=True)
def change_password():
    pass
