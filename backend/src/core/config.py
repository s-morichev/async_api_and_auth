from pathlib import Path
from logging import config as logging_config
from pydantic import BaseSettings, Field
from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env.local"


class Settings(BaseSettings):
    PROJECT_NAME: str = Field('movies', env="BACKEND_PROJECT_NAME")
    DEBUG: bool = Field(False, env="BACKEND_DEBUG")
    REDIS_URI: str = Field(..., env="REDIS_DSN")
    ES_URI: str = Field(..., env="ELK_DSN")


settings = Settings(_env_file=ENV_FILE)

