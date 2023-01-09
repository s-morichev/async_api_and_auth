from flask_jwt_extended import decode_token, create_refresh_token, create_access_token

from ..db.storage import AbstractStorage
from ..db.database import User
from ..utils.utils import device_id_from_name

storage: AbstractStorage


class RefreshError(Exception):
    """Рефреш токен не валидный"""


def tokenize(refresh_token):
    # сохраняем в редис валидный refresh токен с информацией об устройстве, с которого пришел юзер
    token = decode_token(refresh_token)
    user_id = token['sub']
    device_id = token['device_id']
    token_id = token['jti']
    expires = token['exp']
    storage.set_token(user_id, device_id, token_id, expires)


def new_tokens(user: User, device_name):
    """Создаем новые токены при входе"""
    device_id = device_id_from_name(device_name)
    ext_claims = {'name': user.name, 'roles': user.roles_list(), 'device_id': device_id}
    refresh_token = create_refresh_token(identity=user.id, additional_claims=ext_claims)
    access_token = create_access_token(identity=user.id, additional_claims=ext_claims, fresh=True)
    tokenize(refresh_token)

    return access_token, refresh_token


def refresh_tokens(payload: dict):
    """ Создаем новые токены на базе paylod токена (refresh скорее всего)"""

    user_id = payload['sub']
    device_id = payload['device_id']
    old_token_id = payload['jti']

    if not storage.check_token(user_id, device_id, old_token_id):
        raise RefreshError('Invalid refresh token')

    roles = payload['roles']
    user_name = payload['name']
    ext_claims = {'name': user_name, 'roles': roles, 'device_id': device_id}

    refresh_token = create_refresh_token(identity=user_id, additional_claims=ext_claims)
    access_token = create_access_token(identity=user_id, additional_claims=ext_claims)
    tokenize(refresh_token)

    return access_token, refresh_token


def logout(user_id, device_id):
    """стираем сессию в хранилище"""
    storage.remove_session(user_id, device_id)


def is_valid_device(device_name, token_payload):
    """Сверяет хэш имени устройства и device_id в токене"""
    device_id = device_id_from_name(device_name)
    return device_id == token_payload.get("device_id")

def check_token(user_id, device_id, token_id):
    """Проверяем не отозван ли refresh токен"""
    return storage.check_token(user_id, device_id, token_id)


