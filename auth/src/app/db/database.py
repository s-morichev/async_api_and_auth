from abc import ABC, abstractmethod
from typing import Type
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash

import app.models.db_models as data

# ------------------------------------------------------------------------------ #
UserID = UUID


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
    roles: list[Role]

    def roles_list(self) -> list[str]:
        return [role.name for role in self.roles]

    @classmethod
    def from_db(cls, db_user: data.User):
        print(db_user)
        return cls(id=db_user.id,
                   login=db_user.email,
                   password_hash=db_user.password_hash,
                   name=db_user.username,
                   registered=db_user.registered_on,
                   roles=[Role.from_db(db_role) for db_role in db_user.roles])


class UserSession(BaseModel):
    id: UUID
    user_id: UUID
    user_name: str
    login: str
    device_name: str
    device_id: str
    remote_ip: str


# ------------------------------------------------------------------------------ #

# YAGNI
class AbstractDatabase(ABC):
    @abstractmethod
    def add_user(self, login, password, name, registered=datetime.now(tz=timezone.utc)) -> UserID:
        pass

    @abstractmethod
    def is_user_exists(self, login) -> bool:
        pass

    @abstractmethod
    def auth_user(self, login, password) -> User | None:
        pass

    @abstractmethod
    def user_by_id(self, user_id) -> User:
        pass

    @abstractmethod
    def user_by_login(self, login) -> User:
        pass

    @abstractmethod
    def user_add_session(self, user_id, device_name, device_id, remote_ip):
        """сохраняем вход пользователя"""
        pass

    @abstractmethod
    def user_close_session(self, user_id, device_id):
        """сохраняем выход пользователя"""
        pass


# ------------------------------------------------------------------------------ #
class Database(AbstractDatabase):

    def add_user(self, login, password, name, registered=datetime.now(tz=timezone.utc)) -> UserID:
        hash_password = generate_password_hash(password)
        user = data.User(email=login,
                         password_hash=hash_password,
                         username=name,
                         registered_on=registered)

        data.db.session.add(user)
        data.db.session.commit()
        return user.id

    def is_user_exists(self, login) -> bool:
        return data.User.find_by_email(login)

    def auth_user(self, login, password) -> User | None:
        """проводит аутентификацию пользователя"""
        user = self.user_by_login(login)
        if not user or not check_password_hash(user.password_hash, password):
            return None
        return user

    def user_by_login(self, login) -> User | None:
        db_user: data.User = data.User.find_by_email(login)
        if not db_user:
            return None
        else:
            return User.from_db(db_user)

    def user_by_id(self, user_id) -> User | None:
        db_user: data.User = data.User.find_by_id(user_id)
        if not db_user:
            return None
        else:
            return User.from_db(db_user)

    def user_add_session(self, user_id, device_name, device_id, remote_ip):
        pass

    def user_close_session(self, user_id, device_id):
        pass

