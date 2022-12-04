from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings, Field

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env.local"
VAR_DIR = BASE_DIR / "var/"
LOG_DIR = VAR_DIR / "log/"
LOG_FILE = LOG_DIR / "service.log"


class Settings(BaseSettings):
    PROJECT_NAME: str = Field("movies", env="BACKEND_PROJECT_NAME")
    DEBUG: bool = Field(False, env="BACKEND_DEBUG")
    REDIS_URI: str = Field(..., env="REDIS_DSN")
    ES_URI: str = Field(..., env="ELK_DSN")


settings = Settings(_env_file=ENV_FILE)


def create_work_dirs_if_not_exists():
    """
    Create dirs for work
    """
    try:
        if not VAR_DIR.exists():
            print(f"Create dir VAR_DIR {VAR_DIR}")
            VAR_DIR.mkdir(parents=True)
        else:
            if settings.DEBUG:
                print(f"Dir VAR_DIR exists: {VAR_DIR}")

        if not LOG_DIR.exists():
            print(f"Create dir LOG_DIR {LOG_DIR}")
            LOG_DIR.mkdir(parents=True)
        else:
            if settings.DEBUG:
                print(f"Dir LOG_DIR exists: {LOG_DIR}")

    except OSError as e:
        print(f" Error while create dirs: {e}")
        raise


create_work_dirs_if_not_exists()
