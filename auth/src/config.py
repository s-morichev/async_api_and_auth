from datetime import timedelta
from pathlib import Path

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR.parent / ".env"
VAR_DIR = BASE_DIR / "var/"
LOG_DIR = VAR_DIR / "log/"
LOG_FILE = LOG_DIR / "auth.log"


class Config(BaseSettings):
    # PROJECT_NAME: str = Field("auth", env="AUTH_PROJECT_NAME")
    SECRET_KEY: str = Field(..., env="AUTH_SECRET_KEY")
    DEBUG: bool = Field(False, env="AUTH_DEBUG")
    REDIS_URI: str = Field(..., env="REDIS_AUTH_DSN")
    SQLALCHEMY_DATABASE_URI: str = Field(..., env="PG_AUTH_DSN")
    JWT_SECRET_KEY: str = Field(..., env="AUTH_JWT_KEY")
    JWT_COOKIE_SECURE: bool = Field(..., env="AUTH_JWT_COOKIE_SECURE")
    JWT_COOKIE_CSRF_PROTECT: bool = True
    JWT_CSRF_IN_COOKIES: bool = True
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=30)

    class Config:
        env_file = ENV_FILE


class TestConfig(Config):
    TESTING: bool = True
    REDIS_URI: str = Field(..., env="REDIS_AUTH_TEST_DSN")
    SQLALCHEMY_DATABASE_URI: str = Field(..., env="PG_AUTH_TEST_DSN")
    JWT_COOKIE_SECURE: bool = False


flask_config = Config()
test_config = TestConfig()

