import datetime
from http import HTTPStatus

from ..db.storage import AbstractStorage
from ..db.database import AbstractDatabase, User
from ..utils import device_id_from_name
from ..exceptions import HTTPError

# ------------------------------------------------------------------------------ #
storage: AbstractStorage
database: AbstractDatabase


class AuthError(Exception):
    """Общий класс ошибок"""


class CredentialError(AuthError):
    """Ошибка проверки логин/пароль"""


class RegisterError(AuthError):
    """Ошибка регистрации пользователя"""


# ------------------------------------------------------------------------------ #
def auth(email: str, password: str) -> User | None:
    """check user auth and return user if OK"""
    user = database.auth_user(email, password)
    if not user:
        raise CredentialError('Error login/password')
    return user


def add_history(user_id, device_name, action):
    database.add_user_action(user_id, device_name, action)


def get_user_history(user_id) -> list[dict]:
    if (user := database.user_by_id(user_id)) is None:
        raise HTTPError(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    actions = database.get_user_actions(user_id)
    return [action.dict() for action in actions]


def new_session(user_id, device_name: str, remote_ip: str, ttl: int):
    login_at = str(datetime.datetime.now())
    data = {'device_name': device_name, 'remote_ip': remote_ip, 'login_at': login_at}
    device_id = device_id_from_name(device_name)
    storage.set_info(user_id, device_id, data, ttl)
    add_history(user_id, device_name, 'login')


def refresh_session(user_id: str, device_name: str, remote_ip: str, ttl: int):
    data = {'remote_ip': remote_ip}
    device_id = device_id_from_name(device_name)
    storage.set_info(user_id, device_id, data, ttl)
    add_history(user_id, device_name, 'update')


def close_session(user_id: str, device_name: str, remote_ip: str):
    # data = {'remote_ip': remote_ip}
    device_id = device_id_from_name(device_name)
    storage.delete_info(user_id, device_id)
    add_history(user_id, device_name, 'logout')
