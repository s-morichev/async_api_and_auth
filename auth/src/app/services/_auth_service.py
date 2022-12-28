import hashlib
from http import HTTPStatus

from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jti, decode_token
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, flask_config, storage
from app.models.db_models import Role, User

DEFAULT_ROLE = "user"


class CredentialError(Exception):
    pass


def register_user(email: str, password: str, name: str):
    # если существует такой пользователь
    if User.find_by_email(email):
        return
    # if db.session.query(User).filter_by(email=email).first() is not None:

    default_role = db.session.query(Role).filter(Role.name == DEFAULT_ROLE).first()

    password_hash = generate_password_hash(password)
    user = User(email=email, password_hash=password_hash, username=name)
    user.roles.append(default_role)
    db.session.add(user)
    db.session.commit()

    # TODO отправить ссылку подтверждения на почту
    print(user.id)


def login(email: str, password: str, user_agent: str, access_jti: str | None) -> tuple[str, str]:
    #  если юзер пришел на /login с access токеном, то сохраняем его в редис как невалидный, так как будет выдан новый
    # # Не надо
    # if access_jti:
    #     jwt_redis.set(access_jti, "", ex=flask_config.JWT_ACCESS_TOKEN_EXPIRES)

    user = verify_credentials(email, password)
    device_id = hashlib.sha256(user_agent.encode("utf8")).hexdigest()

    # access, refresh = generate_access_refresh_tokens(user.id, device_id, user=user)
    access, refresh = generate_tokens(user, device_id)

    # сохраняем в редис валидный refresh токен с информацией об устройстве, с которого пришел юзер
    token = decode_token(refresh)
    # refresh_jti = get_jti(refresh)
    jti = token['jti']
    expires = token['exp']
    storage.set_token(user.id, device_id, jti, expires)

    # key = str(user.id) + "#" + device_id
    # jwt_redis.set(key, refresh_jti, ex=flask_config.JWT_REFRESH_TOKEN_EXPIRES)

    # TODO добавить в постгрес инфо о логине
    # db_save_session(user_id, user_agent,)
    return access, refresh


def logout(payload):

    user_id = payload["sub"]
    device_id = payload["device_id"]

    # удаляем из хранилища редис сессию
    storage.remove_key(user_id, device_id)

    # # сохраняем в редис невалидный access токен
    # jwt_redis.set(access_jti, "", ex=flask_config.JWT_ACCESS_TOKEN_EXPIRES)
    # # удаляем из редиса валидный refresh токен
    # jwt_redis.delete(refresh_key)

    # TODO добавить в постгрес инфо о логауте


def refresh(refresh_payload):
    old_refresh_jti = refresh_payload["jti"]
    device_id = refresh_payload["device_id"]
    user_id = refresh_payload["sub"]

    if not storage.check_token(user_id, device_id, old_refresh_jti):
        return

    # # удаляем из редиса предыдущий refresh токен
    # jwt_redis.delete(old_refresh_jti)

    access, refresh = refresh_tokens(refresh_payload)
    token = decode_token(refresh)
    jti = token['jti']
    expires = token['exp']

    # сохраняем в редис валидный новый refresh токен с информацией об устройстве, с которого пришел юзер
    storage.set_token(user_id, device_id, jti, expires)
    return access, refresh


def verify_credentials(email: str, password: str) -> User:
    if (user := User.find_by_email(email)) is None:
        # if (user := db.session.query(User).filter_by(email=email).first()) is None:
        raise CredentialError

    if not check_password_hash(user.password_hash, password):
        raise CredentialError

    return user


def generate_tokens(user, device_id):
    """Создаем новые токены"""
    roles = [str(role) for role in user.roles]
    ext_claims = {'name': user.username, 'roles': roles, 'device_id': device_id}
    refresh_token = create_refresh_token(identity=user.id, additional_claims=ext_claims)
    access_token = create_access_token(identity=user.id, additional_claims=ext_claims, fresh=True)

    return access_token, refresh_token


def refresh_tokens(payload: dict):
    """ Создаем новые токены на базе refresh токена"""

    roles = payload.get('roles')
    device_id = payload.get('device_id')
    user_id = payload.get('sub')
    user_name = payload.get('name')
    ext_claims = {'name': user_name, 'roles': roles, 'device_id': device_id}

    refresh_token = create_refresh_token(identity=user_id, additional_claims=ext_claims)
    access_token = create_access_token(identity=user_id, additional_claims=ext_claims)

    return access_token, refresh_token
