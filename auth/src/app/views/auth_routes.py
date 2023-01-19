from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required, set_refresh_cookies, unset_jwt_cookies

from app.services import auth_service, token_service
from app.core.utils import error

auth_bp = Blueprint("auth", __name__)


# ------------------------------------------------------------------------------ #
@auth_bp.post("/login")
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    device_name = request.headers.get("User-Agent")
    remote_ip = request.remote_addr

    if email is None or password is None:
        return error("No email or password", HTTPStatus.BAD_REQUEST)

    try:
        user = auth_service.auth(email, password)

    except auth_service.CredentialError:
        return error("Invalid email or password", HTTPStatus.UNAUTHORIZED)

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


# ------------------------------------------------------------------------------ #
@auth_bp.post("/logout")
@jwt_required()
def logout():
    token = get_jwt()
    user_id = token["sub"]
    device_id = token["device_id"]
    remote_ip = request.remote_addr
    device_name = request.headers.get("User-Agent")

    token_service.remove_token(user_id, device_id)
    auth_service.close_session(user_id, device_name, remote_ip)

    response = jsonify({'msg': 'logout'})
    unset_jwt_cookies(response)

    return response


# ------------------------------------------------------------------------------ #
@auth_bp.route("/refresh", methods=["GET", "POST"])
@jwt_required(refresh=True)
def refresh():
    payload = get_jwt()

    device_name = request.headers.get("User-Agent")
    if not token_service.is_valid_device(device_name, payload):
        return error("Token invalidated", HTTPStatus.UNAUTHORIZED)

    user_id = payload["sub"]
    device_id = payload["device_id"]
    old_token_id = payload["jti"]
    remote_ip = request.remote_addr
    access_token, refresh_token = token_service.refresh_tokens(user_id, device_id, old_token_id)

    # ttl - time of session life
    ttl = token_service.get_refresh_token_expires()
    auth_service.refresh_session(user_id, device_name, remote_ip, ttl)

    response = jsonify(access_token=access_token, refresh_token=refresh_token)
    set_refresh_cookies(response, refresh_token)

    return response


# ------------------------------------------------------------------------------ #
