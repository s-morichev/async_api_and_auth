import hashlib
from http import HTTPStatus
from uuid import UUID

from .exceptions import HTTPError


def device_id_from_name(device_name: str):
    return hashlib.sha256(device_name.encode("utf8")).hexdigest()


def validate_uuid(id_: str) -> None:
    try:
        UUID(id_)
    except ValueError:
        raise HTTPError(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid UUID")