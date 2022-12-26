import hashlib
from http import HTTPStatus

from flask import Blueprint, request, jsonify
from flask_jwt_extended import current_user, get_jwt, jwt_required, set_access_cookies

from app.services import auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email is None or password is None:
        return jsonify({"msg": "No email or password"}), HTTPStatus.BAD_REQUEST

    auth_service.register_user(email, password)
    return jsonify({"msg": "Registered"})


@auth_bp.post("/login")
@jwt_required(optional=True)
def login():

    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user_agent = request.headers.get("User-Agent")
    access_jti = get_jwt().get("jti", None)

    if email is None or password is None:
        return jsonify({"message": "No email or password"}), HTTPStatus.BAD_REQUEST

    try:
        access, refresh = auth_service.login(email, password, user_agent, access_jti)
    except auth_service.CredentialError:
        return jsonify({"message": "Invalid email or password"}), HTTPStatus.UNAUTHORIZED

    # TODO use httponly cookie, add csrf protection
    return jsonify(access_token=access, refresh_token=refresh)


# пример из flask_jwt_extended
@auth_bp.get("/me")
@jwt_required()
def me():
    # We can now access our sqlalchemy User object via `current_user`.
    claims = get_jwt()
    return jsonify(
        id=current_user.id, email=current_user.email, username=current_user.username, role_claims=claims["roles"]
    )


@auth_bp.get("/logout")
@jwt_required()
def logout():
    payload = get_jwt()
    auth_service.logout(payload)
    return jsonify(message="Logged out")


@auth_bp.get("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_agent = request.headers.get("User-Agent")
    device_id = hashlib.sha256(user_agent.encode("utf8")).hexdigest()
    payload = get_jwt()
    if device_id != payload.get("device_id"):
        return jsonify(message="Token has been revoked"), HTTPStatus.UNAUTHORIZED

    access, refresh = auth_service.refresh(payload)
    return jsonify(access_token=access, refresh_token=refresh)


@jwt_required(fresh=True)
def change_email():
    pass


@jwt_required(fresh=True)
def change_password():
    pass
