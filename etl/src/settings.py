from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).parent.parent

# env in project root
ENV_FILE = BASE_DIR / '.env.local'
SCHEMA_FILE_MOVIES = BASE_DIR / 'etc/movies_schema.json'
SCHEMA_FILE_GENRES = BASE_DIR / 'etc/genres_schema.json'
SCHEMA_FILE_PERSONS = BASE_DIR / 'etc/persons_schema.json'

VAR_DIR = BASE_DIR / 'var/'
LOG_DIR = VAR_DIR / 'log/'

STATE_FILE = VAR_DIR / 'etl_state.json'
LOG_FILE = LOG_DIR / 'etl.log'


class Settings(BaseSettings):
    DEBUG: bool = False
    PG_URI: str
    ES_URI: str
    ES_INDEX_MOVIES: str = 'movies'
    ES_INDEX_PERSONS: str = 'persons'
    ES_INDEX_GENRES: str = 'genres'
    ETL_SLEEP_TIME: int = 10
    PG_BATCH_SIZE: int = 500
    ES_BATCH_SIZE: int = 1000  # ES>PG!!!


settings = Settings(_env_file=ENV_FILE)


def create_work_dirs_if_not_exists():
    """
        Create dirs for work
    """
    try:
        if not VAR_DIR.exists():
            print(f'Create dir VAR_DIR {VAR_DIR}')
            VAR_DIR.mkdir(parents=True)
        else:
            if settings.DEBUG:
                print(f'Dir VAR_DIR exists: {VAR_DIR}')

        if not LOG_DIR.exists():
            print(f'Create dir LOG_DIR {LOG_DIR}')
            LOG_DIR.mkdir(parents=True)
        else:
            if settings.DEBUG:
                print(f'Dir LOG_DIR exists: {LOG_DIR}')

    except OSError as e:
        print(f' Error while create dirs: {e}')
        raise


create_work_dirs_if_not_exists()
