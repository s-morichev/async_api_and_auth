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


# @auth_bp.post("/register")
# def register():
#     email = request.json.get("email", None)
#     password = request.json.get("password", None)
#     # если имя не указано, используем e-mail
#     name = request.json.get("name", email)
#
#     if email is None or password is None:
#         return msg("No email or password"), HTTPStatus.BAD_REQUEST
#     try:
#         auth_service.register_user(email, password, name)
#     except auth_service.RegisterError as err:
#         return msg(str(err)), HTTPStatus.CONFLICT
#
#     return msg("Registered")


@auth_bp.post("/login")
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    device_name = request.headers.get("User-Agent")
    remote_ip = request.remote_addr

    if email is None or password is None:
        return msg("No email or password"), HTTPStatus.BAD_REQUEST

    try:
        user = auth_service.auth(email, password)

    except auth_service.CredentialError:
        return msg("Invalid email or password"), HTTPStatus.UNAUTHORIZED

    access_token, refresh_token = token_service.new_tokens(user, device_name)
    # ttl - time of session life
    ttl = token_service.get_refresh_token_expires()
    auth_service.new_session(user.id, device_name, remote_ip, ttl)

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
    claims = get_jwt()
    return jsonify(current_user.dict())


@auth_bp.post("/logout")
@jwt_required()
def logout():
    token = get_jwt()
    user_id = token['sub']
    device_id = token['device_id']
    remote_ip = request.remote_addr
    device_name = request.headers.get("User-Agent")

    token_service.remove_token(user_id, device_id)
    auth_service.close_session(user_id, device_name, remote_ip)

    response = msg("Logged out")
    unset_jwt_cookies(response)

    return response


@auth_bp.route("/refresh",  methods=["GET", "POST"])
@jwt_required(refresh=True)
def refresh():
    payload = get_jwt()

    device_name = request.headers.get("User-Agent")
    if not token_service.is_valid_device(device_name, payload):
        return msg("Token invalidated"), HTTPStatus.UNAUTHORIZED

    user_id = payload['sub']
    device_id = payload['device_id']
    old_token_id = payload['jti']
    remote_ip = request.remote_addr
    access_token, refresh_token = token_service.refresh_tokens(user_id, device_id, old_token_id)

    # ttl - time of session life
    ttl = token_service.get_refresh_token_expires()
    auth_service.refresh_session(user_id, device_name, remote_ip, ttl)

    response = jsonify(access_token=access_token, refresh_token=refresh_token)
    set_refresh_cookies(response, refresh_token)

    return response


@jwt_required(fresh=True)
def change_email():
    pass


@jwt_required(fresh=True)
def change_password():
    pass
