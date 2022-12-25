from pathlib import Path

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR.parent / ".env.local"


class Settings(BaseSettings):
    REDIS_URI: str = Field(..., env="REDIS_BACKEND_DSN")
    ES_URI: str = Field(..., env="ELK_MOVIES_DSN")
    API_URI: str = Field(..., env="API_DSN")
    ES_MOVIES_INDEX: str = "movies"
    ES_GENRES_INDEX: str = "genres"
    ES_PERSONS_INDEX: str = "persons"

    @property
    def ES_ALL_INDICES(self) -> list[str]:
        return [self.ES_MOVIES_INDEX, self.ES_PERSONS_INDEX, self.ES_GENRES_INDEX]


settings = Settings(_env_file=ENV_FILE)
