from uuid import UUID

from ..db.database import AbstractDatabase, User, Role

database: AbstractDatabase


def get_all_roles():
    roles_list = database.get_all_roles()
    result = [role.dict() for role in roles_list]
    return result


def add_role(name: str) -> Role:
    new_role: Role = database.add_role(name)
    return new_role.dict()


def delete_role(role_id: UUID):
    database.delete_role(role_id)


def update_role(role_id: UUID, new_name: str):
    database.update_role(role_id, new_name)


def get_role(role_id: UUID):
    role = database.role_by_id(role_id)
    return role.dict()


def get_user_roles(user_id: UUID):
    roles_list = database.get_user_roles(user_id)
    result = [role.dict() for role in roles_list]
    return result


def add_user_role(user_id: UUID, role_id: UUID):
    roles_list = database.add_user_role(user_id, role_id)
    result = [role.dict() for role in roles_list]
    return result


def delete_user_role(user_id: UUID, role_id: UUID):
    roles_list = database.delete_user_role(user_id, role_id)
    result = [role.dict() for role in roles_list]
    return result
