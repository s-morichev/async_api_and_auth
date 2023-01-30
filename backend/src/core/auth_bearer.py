import logging
from http import HTTPStatus

import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings
from models.token import AccessTokenPayload

logger = logging.getLogger(__name__)

JWT_SECRET = settings.JWT_SECRET_KEY
JWT_ALGORITHM = "HS256"


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> AccessTokenPayload:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid authorization code.")
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid authentication scheme.")

        try:
            decoded_token = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.PyJWTError:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token or expired token.")

        logger.debug(f'jwt-token payload: {decoded_token}')
        return AccessTokenPayload(**decoded_token)


jwt_bearer = JWTBearer()
