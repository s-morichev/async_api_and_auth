from http import HTTPStatus

from flask import Blueprint, abort, make_response, request

from app.services import role_service

role_bp = Blueprint("role", __name__)

# TODO сделать декоратор для проверки access токена
# @role_bp.get("/")
# @permission_required(Permission.CRUD_ROLES)
# def all_role():


@role_bp.get("/")
def all_role():
    # проверяем валидность токена, если не валидный - возвращаем unauthorithed
    # проверяем разрешение, если не подходит - возвращаем forbidden
    # возвращаем роли
    return role_service.get_all_roles()
