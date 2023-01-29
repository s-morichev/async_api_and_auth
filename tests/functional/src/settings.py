from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR.parent / ".env.local"

# pytest видимо сам прогружает .env где найдет, а находит в корне...
# поэтому явно загружаем нужный файл для локального запуска
load_dotenv(ENV_FILE, override=True)


class Settings(BaseSettings):
    REDIS_URI: str = Field(..., env="REDIS_BACKEND_DSN")
    ES_URI: str = Field(..., env="ELK_MOVIES_DSN")
    BACKEND_URI: str = Field(..., env="BACKEND_DSN")
    ES_MOVIES_INDEX: str = "movies"
    ES_GENRES_INDEX: str = "genres"
    ES_PERSONS_INDEX: str = "persons"
    JWT_KEY: str = Field(..., env="AUTH_JWT_KEY")

    @property
    def ES_ALL_INDICES(self) -> list[str]:
        return [self.ES_MOVIES_INDEX, self.ES_PERSONS_INDEX, self.ES_GENRES_INDEX]


settings = Settings()
