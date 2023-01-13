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
    device_name: str
    device_id: str
    remote_ip: str

    @classmethod
    def from_db(cls, db_session: data.UserSession):
        return cls(id=db_session.id,
                   user_id=db_session.user_id,
                   device_name=db_session.device_name,
                   device_id=db_session.device_id,
                   remote_ip=db_session.remote_ip)






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
    def user_add_session(self, user_id, device_name, device_id, remote_ip, expires):
        """сохраняем вход пользователя"""
        pass

    @abstractmethod
    def user_close_session(self, user_id, device_id):
        """сохраняем выход пользователя"""
        pass

    @abstractmethod
    def user_refresh_session(self, user_id, device_id, expires):
        """ сохраняем информацию об активности и продлеваем сессию"""
        pass

    @abstractmethod
    def get_all_roles(self):
        pass

    @abstractmethod
    def add_role(self, name):
        pass

    @abstractmethod
    def is_role_exists(self, name):
        pass

    @abstractmethod
    def delete_role(self, role_id: UUID):
        pass

    @abstractmethod
    def update_role(self, role_id: UUID, new_name: str):
        pass

    @abstractmethod
    def role_by_id(self, role_id: UUID) -> Role:
        pass

    @abstractmethod
    def get_user_roles(self, user_id):
        pass

    @abstractmethod
    def add_user_role(self, user_id, role_id):
        pass

    @abstractmethod
    def delete_user_role(self, user_id, role_id):
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

    def user_add_session(self, user_id, device_name, device_id, remote_ip, expires):
        db_user_session = data.UserSession(user_id=user_id,
                                   device_id=device_id,
                                   device_name=device_name,
                                   remote_ip=remote_ip,
                                   active_till=expires)

        data.db.session.add(db_user_session)
        data.db.session.commit()
        session = UserSession.from_db(db_user_session)
        return session

    def user_close_session(self, user_id, device_id):
        pass

    def user_refresh_session(self, user_id, device_id, expires):
        pass

    def get_all_roles(self):
        query = data.Role.query.all()
        roles = [Role.from_db(db_role) for db_role in query]
        return roles

    def add_role(self, name):
        db_role = data.Role(name=name)
        data.db.session.add(db_role)
        data.db.session.commit()
        return Role.from_db(db_role)

    def is_role_exists(self, name):
        return data.Role.find_by_name(name)

    def delete_role(self, role_id: UUID):
        data.Role.query.filter_by(id=role_id).delete()
        data.db.session.commit()

    def update_role(self, role_id: UUID, new_name: str):
        data.Role.query.filter_by(id=role_id).update({'name': new_name})
        data.db.session.commit()

    def role_by_id(self, role_id: UUID) -> Role:
        db_role = data.Role.query.filter_by(id=role_id).first()
        return Role.from_db(db_role)

    def get_user_roles(self, user_id):
        query = data.User.find_by_id(user_id).roles
        roles = [Role.from_db(db_role) for db_role in query]
        return roles

    def add_user_role(self, user_id, role_id):
        role = data.Role.query.filter_by(id=role_id).first()
        user = data.User.find_by_id(user_id)
        user.roles.append(role)
        data.db.session.commit()
        return [Role.from_db(db_role) for db_role in user.roles]

    def delete_user_role(self, user_id, role_id):
        role = data.Role.query.filter_by(id=role_id).first()
        user = data.User.find_by_id(user_id)
        user.roles.remove(role)
        data.db.session.commit()
        return [Role.from_db(db_role) for db_role in user.roles]





