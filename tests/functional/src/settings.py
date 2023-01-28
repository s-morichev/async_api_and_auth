from pathlib import Path

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR.parent / ".env.local"


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


settings = Settings(_env_file=ENV_FILE)
