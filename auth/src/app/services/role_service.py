from http import HTTPStatus
from uuid import UUID

from ..db.database import AbstractDatabase, User, Role
from ..exceptions import HTTPError

database: AbstractDatabase


class RoleError(Exception):
    """Ошибки, связанные с ролями"""


def get_all_roles():
    roles_list = database.get_all_roles()
    result = [role.dict() for role in roles_list]
    return result


def add_role(name: str) -> Role:
    if database.is_role_exists(name):
        raise RoleError("Role exists")
    new_role: Role = database.add_role(name)
    return new_role.dict()


def delete_role(role_id: UUID):
    if database.role_by_id(role_id) is None:
        raise HTTPError(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")
    database.delete_role(role_id)


def update_role(role_id: UUID, new_name: str):
    if database.role_by_id(role_id) is None:
        raise HTTPError(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")
    database.update_role(role_id, new_name)


def get_role(role_id: UUID):
    if (role := database.role_by_id(role_id)) is None:
        raise HTTPError(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")
    return role.dict()


def get_user_roles(user_id: UUID):
    if database.user_by_id(user_id) is None:
        raise HTTPError(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    roles_list = database.get_user_roles(user_id)
    result = [role.dict() for role in roles_list]
    return result


def add_user_role(user_id: UUID, role_id: UUID):
    if database.user_by_id(user_id) is None:
        raise HTTPError(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    if database.role_by_id(role_id) is None:
        raise HTTPError(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")
    roles_list = database.add_user_role(user_id, role_id)
    result = [role.dict() for role in roles_list]
    return result


def delete_user_role(user_id: UUID, role_id: UUID):
    if database.user_by_id(user_id) is None:
        raise HTTPError(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    if database.role_by_id(role_id) is None:
        raise HTTPError(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")
    roles_list = database.delete_user_role(user_id, role_id)
    result = [role.dict() for role in roles_list]
    return result
