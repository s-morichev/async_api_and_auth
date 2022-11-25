import os
import pathlib
from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

# Настройки Redis
REDIS_DSN = os.getenv("REDIS_DSN")

# Настройки Elasticsearch
ELK_DSN = os.getenv("ELK_DSN")

# Корень проекта (папка в которой находится main.py)
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
