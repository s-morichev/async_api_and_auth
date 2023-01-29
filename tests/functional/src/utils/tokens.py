import time

import jwt

from ..settings import settings


def generate_access_token(exp_delta: int, roles: list[str], key: str | None = None) -> str:
    payload = {
        "fresh": True,
        "iat": time.time() - 100,
        "jti": "6928145b-b576-499c-a8b7-4cb6ad3a82a9",
        "type": "access",
        "sub": "1a63a6f5-5103-4965-8f2a-6a8454228356",
        "nbf": time.time() - 100,
        "csrf": "fb04d08c-c54f-44b2-a6f6-2210cd98c9aa",
        "exp": int(time.time()) + exp_delta,
        "name": "test_user",
        "roles": roles,
        "device_id": "device_id",
    }
    if key is None:
        key = settings.JWT_KEY
    token = jwt.encode(payload, key, algorithm="HS256")
    return token
