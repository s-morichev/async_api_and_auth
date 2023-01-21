from abc import ABC, abstractmethod
from datetime import datetime, timezone
from http import HTTPStatus
from uuid import UUID

from pydantic import BaseModel
from werkzeug.security import check_password_hash, generate_password_hash

import app.models.db_models as data
from app.core.utils import error

# ------------------------------------------------------------------------------ #
UserID = UUID


class DatabaseError(Exception):
    pass


class NotFoundUser(DatabaseError):
    pass


class UserAddError(DatabaseError):
    pass


class UserChangeError(DatabaseError):
    pass


class Role(BaseModel):
    id: UUID
    name: str

    @classmethod
    def from_db(cls, db_role: data.Role):
        return cls(id=db_role.id, name=db_role.name)


class User(BaseModel):
    id: UserID
    login: str
    password_hash: str
    name: str
    registered: datetime
    is_confirmed: bool
    is_root: bool
    roles: list[Role]

    def roles_list(self) -> list[str]:
        return [role.name for role in self.roles]

    @classmethod
    def from_db(cls, db_user: data.User):
        return cls(
            id=db_user.id,
            login=db_user.email,
            password_hash=db_user.password_hash,
            name=db_user.username,
            registered=db_user.registered_on,
            is_confirmed=db_user.is_confirmed,
            is_root=db_user.is_root,
            roles=[Role.from_db(db_role) for db_role in db_user.roles],
        )


class UserSession(BaseModel):
    id: UUID
    user_id: UUID
    device_name: str
    device_id: str
    remote_ip: str

    @classmethod
    def from_db(cls, db_session: data.UserSession):
        return cls(
            id=db_session.id,
            user_id=db_session.user_id,
            device_name=db_session.device_name,
            device_id=db_session.device_id,
            remote_ip=db_session.remote_ip,
        )


class UserAction(BaseModel):
    id: UUID
    user_id: UUID
    device_name: str
    timestamp: datetime
    action: str

    @classmethod
    def from_db(cls, db_user_action: data.UserAction):
        return cls(
            id=db_user_action.id,
            user_id=db_user_action.user_id,
            device_name=db_user_action.device_name,
            timestamp=db_user_action.action_time,
            action=db_user_action.action_type,
        )


# ------------------------------------------------------------------------------ #

# YAGNI
class AbstractDatabase(ABC):
    @abstractmethod
    def add_user(self, login, password, name, registered=datetime.now(tz=timezone.utc)) -> User:
        pass

    @abstractmethod
    def change_user_login(self, user_id: UserID, new_login: str) -> User:
        pass

    @abstractmethod
    def change_user_password(self, user_id: UserID, new_password: str) -> User:
        pass

    @abstractmethod
    def change_user_name(self, user_id: UserID, new_name: str) -> User:
        pass

    @abstractmethod
    def change_user(self, user_id: UserID, new_name: str, new_password: str) -> User:
        pass

    @abstractmethod
    def is_user_exists(self, login: str) -> bool:
        pass

    @abstractmethod
    def auth_user(self, login: str, password: str) -> User | None:
        pass

    @abstractmethod
    def user_by_login(self, login: str) -> User | None:
        pass

    @abstractmethod
    def user_by_id(self, user_id: UserID) -> User | None:
        pass

    @abstractmethod
    def get_all_roles(self) -> list[Role]:
        pass

    @abstractmethod
    def add_role(self, name: str) -> Role:
        pass

    @abstractmethod
    def is_role_exists(self, name: str) -> bool:
        pass

    @abstractmethod
    def get_role_by_name(self, name: str) -> Role | None:
        pass

    @abstractmethod
    def delete_role(self, role_id: UUID) -> bool:
        pass

    @abstractmethod
    def update_role(self, role_id: UUID, new_name: str) -> Role | None:
        pass

    @abstractmethod
    def role_by_id(self, role_id: UUID) -> Role | None:
        pass

    @abstractmethod
    def get_user_roles(self, user_id: UserID) -> list[Role | None]:
        pass

    @abstractmethod
    def add_user_role(self, user_id: UserID, role_id: UUID) -> list[Role] | None:
        pass

    @abstractmethod
    def delete_user_role(self, user_id: UserID, role_id: UUID):
        pass

    @abstractmethod
    def add_user_action(self, user_id: UserID, device_name: str, action: str) -> UserAction:
        pass

    @abstractmethod
    def get_user_actions(self, user_id: UserID) -> list[UserAction | None]:
        pass


# ------------------------------------------------------------------------------ #
class Database(AbstractDatabase):
    def add_user(self, login, password, name, registered=datetime.now(tz=timezone.utc)) -> User:
        hash_password = generate_password_hash(password)

        if not name:
            name = login

        db_user = data.User(email=login, password_hash=hash_password, username=name, registered_on=registered)

        data.db.session.add(db_user)
        data.db.session.commit()
        return User.from_db(db_user)

    def change_user_login(self, user_id: UserID, new_login: str) -> User:
        db_user = data.User.find_by_id(user_id)

        if new_login == db_user.email:
            return User.from_db(db_user)

        if self.is_user_exists(new_login):
            error("user with this login already exists", HTTPStatus.CONFLICT)

        db_user.email = new_login
        data.db.session.add(db_user)
        data.db.session.commit()
        return User.from_db(db_user)

    def change_user_password(self, user_id: UserID, new_password: str) -> User:
        db_user = data.User.find_by_id(user_id)

        hash_password = generate_password_hash(new_password)
        db_user.password_hash = hash_password
        data.db.session.add(db_user)
        data.db.session.commit()
        return User.from_db(db_user)

    def change_user_name(self, user_id: UserID, new_name: str) -> User:
        db_user = data.User.find_by_id(user_id)
        db_user.username = new_name
        data.db.session.add(db_user)
        data.db.session.commit()
        return User.from_db(db_user)

    def change_user(self, user_id: UserID, new_name: str | None, new_password: str | None) -> User:
        db_user = data.User.find_by_id(user_id)
        if not new_name and not new_password:
            return User.from_db(db_user)

        if new_name:
            db_user.username = new_name

        if new_password:
            hash_password = generate_password_hash(new_password)
            db_user.password_hash = hash_password

        data.db.session.add(db_user)
        data.db.session.commit()
        return User.from_db(db_user)

    def is_user_exists(self, login: str) -> bool:
        return data.User.find_by_email(login)

    def auth_user(self, login: str, password: str) -> User | None:
        """проводит аутентификацию пользователя"""
        user = self.user_by_login(login)
        if not user or not check_password_hash(user.password_hash, password):
            return None
        return user

    def user_by_login(self, login: str) -> User | None:
        db_user: data.User = data.User.find_by_email(login)
        if not db_user:
            return None
        else:
            return User.from_db(db_user)

    def user_by_id(self, user_id: UserID) -> User | None:
        db_user: data.User = data.User.find_by_id(user_id)
        if db_user is None:
            return None

        return User.from_db(db_user)

    def get_all_roles(self) -> list[Role]:
        query = data.Role.query.all()
        roles = [Role.from_db(db_role) for db_role in query]
        return roles

    def add_role(self, name: str) -> Role:
        db_role = data.Role(name=name)
        data.db.session.add(db_role)
        data.db.session.commit()
        return Role.from_db(db_role)

    def is_role_exists(self, name: str) -> bool:
        return bool(data.Role.find_by_name(name))

    def get_role_by_name(self, name: str) -> Role | None:
        db_role = data.Role.find_by_name(name)
        if not db_role:
            return None
        return Role.from_db(db_role)

    def delete_role(self, role_id: UUID) -> bool:
        if data.Role.find_by_id(role_id) is None:
            return False

        data.Role.query.filter_by(id=role_id).delete()
        data.db.session.commit()
        return True

    def update_role(self, role_id: UUID, new_name: str) -> Role | None:
        if (db_role := data.Role.find_by_id(role_id)) is None:
            return None

        db_role.name = new_name
        data.db.session.commit()
        return Role.from_db(db_role)

    def role_by_id(self, role_id: UUID) -> Role | None:
        if (db_role := data.Role.find_by_id(role_id)) is None:
            return None
        return Role.from_db(db_role)

    def get_user_roles(self, user_id: UserID) -> list[Role | None]:
        query = data.User.find_by_id(user_id).roles
        roles = [Role.from_db(db_role) for db_role in query]
        return roles

    def add_user_role(self, user_id: UserID, role_id: UUID) -> list[Role] | None:
        role = data.Role.query.filter_by(id=role_id).first()
        if role is None:
            return None
        user = data.User.find_by_id(user_id)
        if user is None:
            return None
        user.roles.append(role)
        data.db.session.commit()
        return [Role.from_db(db_role) for db_role in user.roles]

    def delete_user_role(self, user_id: UserID, role_id: UUID):
        role = data.Role.query.filter_by(id=role_id).first()
        if role is None:
            return None
        user = data.User.find_by_id(user_id)
        if user is None:
            return None
        user.roles.remove(role)
        data.db.session.commit()
        return [Role.from_db(db_role) for db_role in user.roles]

    def add_user_action(self, user_id: UserID, device_name: str, action: str) -> UserAction:
        db_user_action = data.UserAction(user_id=user_id, device_name=device_name, action_type=action)
        data.db.session.add(db_user_action)
        data.db.session.commit()
        return UserAction.from_db(db_user_action)

    def get_user_actions(self, user_id: UserID) -> list[UserAction | None]:
        actions = data.UserAction.by_user_id(user_id)
        result = [UserAction.from_db(db_action) for db_action in actions]
        return result
