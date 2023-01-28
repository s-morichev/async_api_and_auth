from uuid import UUID

from core.core_model import CoreModel


class AccessTokenPayload(CoreModel):
    """Access token payload"""

    fresh: bool
    iat: int
    jti: UUID
    type: str
    sub: UUID
    nbf: int
    csrf: UUID
    exp: int
    name: str
    roles: list[str]
    device_id: str
