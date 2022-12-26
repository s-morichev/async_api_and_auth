import hashlib
from http import HTTPStatus

from flask_jwt_extended import create_access_token, create_refresh_token, get_jti
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, flask_config, jwt_redis
from app.models.db_models import Role, User

DEFAULT_ROLE = "user"


class CredentialError(Exception):
    pass


def register_user(email: str, password: str):
    if db.session.query(User).filter_by(email=email).first() is not None:
        return

    default_role = db.session.query(Role).filter(Role.name == DEFAULT_ROLE).first()

    password_hash = generate_password_hash(password)
    user = User(email=email, password_hash=password_hash)
    user.roles.append(default_role)
    db.session.add(user)
    db.session.commit()

    # TODO отправить ссылку подтверждения на почту
    print(user.id)


def login(email: str, password: str, user_agent: str, access_jti: str | None) -> tuple[str, str]:
    # если юзер пришел на /login с access токеном, то сохраняем его в редис как невалидный, так как будет выдан новый
    if access_jti:
        jwt_redis.set(access_jti, "", ex=flask_config.JWT_ACCESS_TOKEN_EXPIRES)

    user = verify_credentials(email, password)
    device_id = hashlib.sha256(user_agent.encode("utf8")).hexdigest()

    access, refresh = generate_access_refresh_tokens(user.id, device_id, user=user)

    # сохраняем в редис валидный refresh токен с информацией об устройстве, с которого пришел юзер
    refresh_jti = get_jti(refresh)
    value = str(user.id) + "#" + device_id
    jwt_redis.set(refresh_jti, value, ex=flask_config.JWT_REFRESH_TOKEN_EXPIRES)

    # TODO добавить в постгрес инфо о логине

    return access, refresh


def logout(access_payload):
    access_jti = access_payload["jti"]
    refresh_jti = access_payload["refresh_jti"]

    # сохраняем в редис невалидный access токен
    jwt_redis.set(access_jti, "", ex=flask_config.JWT_ACCESS_TOKEN_EXPIRES)
    # удаляем из редиса валидный refresh токен
    jwt_redis.delete(refresh_jti)

    # TODO добавить в постгрес инфо о логауте


def refresh(refresh_payload):
    old_refresh_jti = refresh_payload["jti"]
    device_id = refresh_payload["device_id"]
    user_id = refresh_payload["sub"]

    # удаляем из редиса предыдущий refresh токен
    jwt_redis.delete(old_refresh_jti)

    access, refresh = generate_access_refresh_tokens(user_id, device_id)

    # сохраняем в редис валидный новый refresh токен с информацией об устройстве, с которого пришел юзер
    refresh_jti = get_jti(refresh)
    value = user_id + "#" + device_id
    jwt_redis.set(refresh_jti, value, ex=flask_config.JWT_REFRESH_TOKEN_EXPIRES)

    return access, refresh


def verify_credentials(email: str, password: str) -> User:
    if (user := db.session.query(User).filter_by(email=email).first()) is None:
        raise CredentialError

    if not check_password_hash(user.password_hash, password):
        raise CredentialError

    return user


def generate_access_refresh_tokens(user_id, device_id, user=None):
    # чтобы не делать лишний запрос в постгрес при логине
    # так как только что проверили пароль, получив при этом свежего пользователя из постгреса
    if user is None:
        user = db.session.query(User).get(user_id)

    refresh_claims = {"device_id": device_id}
    refresh_token = create_refresh_token(identity=user.id, additional_claims=refresh_claims)

    access_claims = {"roles": [str(role) for role in user.roles], "refresh_jti": get_jti(refresh_token)}
    access_token = create_access_token(identity=user.id, additional_claims=access_claims)

    return access_token, refresh_token
