import hashlib
from functools import wraps

from flask_jwt_extended import get_jwt, jwt_required
from flask_jwt_extended.exceptions import NoAuthorizationError

from http import HTTPStatus
from uuid import UUID
from app.exceptions import HTTPError
from app.utils import constants


def device_id_from_name(device_name: str):
    return hashlib.sha256(device_name.encode("utf8")).hexdigest()


def jwt_accept_roles(roles_list: str | list[str]):
    """
    decorator for routers with accepted roles

    :param roles_list - list of accepted roles like ["user","admin"]
                        or string like "user, admin"
    Grant access if roles_list INTERSECT user_roles NOT NULL
    """

    def decorator(f):
        @jwt_required()
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if isinstance(roles_list, str):
                accepted_roles = list(map(str.strip, roles_list.split(',')))
            else:
                accepted_roles = roles_list

            token = get_jwt()
            roles = token.get('roles', [])
            # if superuser - dont check roles
            if constants.ROOT_ROLE not in roles:
                roles_intersect = set(accepted_roles) & set(roles)
                if not roles_intersect:
                    raise NoAuthorizationError(f'Only roles {accepted_roles} accepted')

            rv = f(*args, **kwargs)
            return rv

        return decorated_function

    return decorator


def validate_uuids(*args: str) -> None:
    for id_ in args:
        try:
            UUID(id_)
        except ValueError:
            raise HTTPError(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid UUID")