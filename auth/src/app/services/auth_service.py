
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


def login(email: str, password: str, device_name: str, remote_ip=None) -> User:
    user = database.auth_user(email, password)
    if not user:
        raise CredentialError('Error login/password')

    device_id = device_id_from_name(device_name)
    #TODO return UserSession
    database.user_add_session(user.id, device_name, device_id, remote_ip)
    return user


def logout(user_id, device_id):
    database.user_close_session(user_id, device_id)


def refresh(user_id, device_id):
    """ можно сделать апдейт в базе если надо"""
    pass
