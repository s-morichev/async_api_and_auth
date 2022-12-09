# Базовый образ с общими системными зависимостями для dev и prod
FROM python:3.10.8-slim as python-base
ARG APP_NAME
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONPATH="/opt/app:$PYTHONPATH"

# Здесь может быть устновка системных пакетов, например gcc для psycopg2

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /opt/app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src .

ENTRYPOINT ["sh", "-c", "python3 ./utils/wait_for_backend.py \
                         && python3 ./utils/wait_for_redis.py \
                         && python3 ./utils/wait_for_es.py \
                         && pytest ."]
