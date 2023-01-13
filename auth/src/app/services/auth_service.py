from ..db.storage import AbstractStorage
from ..db.database import AbstractDatabase, User
from ..utils.utils import device_id_from_name

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
def register_user(email: str, password: str, name: str):
    # если существует такой пользователь
    if database.is_user_exists(email):
        raise RegisterError('Same login exists')

    database.add_user(email, password, name)
    # TODO отправить ссылку подтверждения на почту
    # можно давать пользователю роль NEW_USER, выдавать короткий токен и ждать подтверждения почты
    # mailer.send_notification(email)


def auth(email: str, password: str) -> User | None:
    """check user auth and return user if OK"""
    user = database.auth_user(email, password)
    if not user:
        raise CredentialError('Error login/password')
    return user


def login(user_id, device_name: str, remote_ip, expires):
    """save info about new user session"""
    device_id = device_id_from_name(device_name)
    # TODO return UserSession
    database.user_add_session(user_id, device_name, device_id, remote_ip, expires)


def logout(user_id, device_id):
    """save info about close user session"""
    database.user_close_session(user_id, device_id)


def refresh(user_id, device_id, expires):
    """ можно сделать апдейт в базе если надо"""
    database.user_refresh_session(user_id, device_id, expires)
