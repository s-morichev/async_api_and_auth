import json
from http import HTTPStatus

from flask_jwt_extended import create_access_token, create_refresh_token, decode_token

import config
from app.core.utils import device_id_from_name
from app.db.database import User
from app.db.storage import AbstractStorage
from app.core.utils import error

storage: AbstractStorage


# ------------------------------------------------------------------------------ #
def tokenize(refresh_token: str):
    # сохраняем в редис валидный refresh токен с информацией об устройстве, с которого пришел юзер
    token = decode_token(refresh_token)
    user_id = token["sub"]
    device_id = token["device_id"]
    token_id = token["jti"]
    token_expires_at = token["exp"]
        storage.set_token(user_id, device_id, token_id, token_expires_at)


def new_tokens(user: User, device_name: str) -> tuple[str, str]:
    """Создаем новые токены при входе"""
    device_id = device_id_from_name(device_name)

    # создаем или обновляем payload в хранилище
    payload = {"name": user.name, "roles": user.roles_list()}

    storage.set_payload(str(user.id), json.dumps(payload))
    ext_claims = payload | {"device_id": device_id}
    refresh_token = create_refresh_token(identity=user.id, additional_claims=ext_claims)
    access_token = create_access_token(identity=user.id, additional_claims=ext_claims, fresh=True)
    tokenize(refresh_token)
    storage.add_device(user.id, device_id)

    return access_token, refresh_token


def refresh_tokens(user_id: str, device_id: str, old_token_id: str) -> tuple[str, str]:
    """Создаем новые токены"""

    if not storage.check_token(user_id, device_id, old_token_id):
        error("Invalid refresh token", HTTPStatus.UNAUTHORIZED)

    # roles = payload['roles']
    # user_name = payload['name']
    # берем payload из хранилища. Возможно он даже изменился за это время)
    payload = json.loads(storage.get_payload(str(user_id)))
    ext_claims = payload | {"device_id": device_id}

    refresh_token = create_refresh_token(identity=user_id, additional_claims=ext_claims)
    access_token = create_access_token(identity=user_id, additional_claims=ext_claims)
    tokenize(refresh_token)

    return access_token, refresh_token


def remove_token(user_id: str, device_id: str):
    """стираем сессию в хранилище"""
    storage.remove_token(user_id, device_id)
    storage.remove_device(user_id, device_id)


def refresh_devices(user_id: str):
    """убираем устройства для которых отсутствует запись с токеном"""
    devices = storage.get_devices(user_id)
    if not devices:
        return

    closed = []
    for device in devices:
        if not storage.exist_token(user_id, device):
            closed += [device]

    for device_id in closed:
        storage.remove_device(user_id, device_id)


def is_valid_device(device_name: str, token_payload: dict):
    """Сверяет хэш имени устройства и device_id в токене"""
    device_id = device_id_from_name(device_name)
    return device_id == token_payload.get("device_id")


def check_token(user_id: str, device_id: str, token_id: str):
    """Проверяем не отозван ли refresh токен"""
    return storage.check_token(user_id, device_id, token_id)


def get_refresh_token_expires() -> int:
    """return time of life refresh_token"""
    return config.flask_config.JWT_REFRESH_TOKEN_EXPIRES


def set_payload(user_id: str, new_payload: dict):
    storage.set_payload(user_id, json.dumps(new_payload))


def close_all(user_id: str):
    """Выходит со всех устройств"""
    devices = storage.get_devices(user_id)
    for device_id in devices:
        remove_token(user_id, device_id)
    storage.clear_devices(user_id)


def get_user_sessions(user_id: str):
    refresh_devices(user_id)
    devices = storage.get_devices(user_id)
    if not devices:
        return []

    sessions = []
    for device_id in devices:
        info = storage.get_info(user_id, device_id)
        sessions += [info]
    return sessions
