from http import HTTPStatus

from flask import Blueprint, abort, make_response, request

from app.services import auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    email = request.get_json()["email"]
    password = request.get_json()["password"]
    try:
        access, refresh = auth_service.verify_credentials(email, password)
    except Exception:
        # TODO вернуть response без html
        abort(HTTPStatus.UNAUTHORIZED, description="Invalid email ot password")

    # TODO сделать модели для возвращаемых данных
    body = {"body": {"access_token": access, "refresh_token": refresh}}

    resp = make_response(body, HTTPStatus.OK)
    resp.set_cookie(key="refreshToken", value=refresh, httponly=True)
    return resp


def logout(access_token):
    pass


def refresh_tokens(refresh_token):
    pass


def register(email, passoword, username=None):
    pass


def change_email():
    pass


def change_password():
    pass
