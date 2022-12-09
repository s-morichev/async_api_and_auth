from pathlib import Path

from pydantic import BaseSettings, Field
BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / '.env.local'


class Settings(BaseSettings):
    REDIS_DSN: str = Field('redis', env='REDIS_DSN')
    ELK_DSN: str = Field('es', env='ELK_DSN')
    SERVICE_URL: str = Field('http://127.0.0.1:8000', env='BACKEND_DSN')


settings = Settings(_env_file=ENV_FILE)
