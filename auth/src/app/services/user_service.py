from http import HTTPStatus
from uuid import UUID
from ..db.database import AbstractDatabase, User
import app.services.token_service as token_srv
from ..exceptions import HTTPError

database: AbstractDatabase


class UserError(Exception):
    """Общий класс ошибок"""


class RegisterError(UserError):
    """Ошибка регистрации пользователя"""


def add_user(email: str, password: str, name: str) -> dict:
    # если существует такой пользователь
    if database.is_user_exists(email):
        raise HTTPError(status_code=HTTPStatus.CONFLICT, detail="User with this email already registered.")

    user = database.add_user(email, password, name)
    # TODO отправить ссылку подтверждения на почту
    # можно давать пользователю роль NEW_USER, выдавать короткий токен и ждать подтверждения почты
    # mailer.send_notification(email)
    return user.dict(exclude={'password_hash'})


def change_user(user_id: UUID, new_email: str | None, new_password: str | None, new_name: str | None) -> dict:
    user: User = database.user_by_id(user_id)
    if user is None:
        raise HTTPError(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    # очень плохо, три транзакции!!!
    if new_email:
        user = database.change_user_login(user.id, new_email)

    if new_password:
        user = database.change_user_password(user.id, new_password)

    if new_name:
        user = database.change_user_name(user.id, new_name)

    return user.dict(exclude={'password_hash'})


def get_user_by_id(user_id: UUID) -> dict:
    if (user := database.user_by_id(user_id)) is None:
        raise HTTPError(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user.dict(exclude={'password_hash'})


def get_user_sessions(user_id: UUID) -> list[dict]:
    get_user_by_id(user_id)  # проверка что пользователь существует
    return token_srv.get_user_sessions(user_id)

def get_user_history(user_id: UUID) -> list[dict]:
    return token_srv.get_user_sessions(user_id)
