ARG APP_NAME=backend

# Базовый образ с общими системными зависимостями для dev и prod
FROM python:3.10.8-slim as python-base
ARG APP_NAME
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONPATH="/opt:$PYTHONPATH"

RUN apt-get update \
    && apt-get --no-install-recommends install -y \
    netcat \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Билдер для установки Python пакетов и необходимых системных зависимостей
FROM python-base as builder-base
ARG APP_NAME

# Здесь может быть устновка системных пакетов, например gcc для psycopg2

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /opt/${APP_NAME}
COPY ./${APP_NAME}/requirements.txt .
RUN pip install -r requirements.txt

# development образ
FROM python-base as development
ARG APP_NAME

# Копируем python пакеты для продакшена из билдера
COPY --from=builder-base /opt/venv/ /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# Устанавливаем dev python пакеты
WORKDIR /opt/${APP_NAME}
#COPY ./${APP_NAME}/requirements.dev.txt .
#RUN pip install -r requirements.dev.txt

COPY ./docker/${APP_NAME}/entrypoint.sh ./docker/wait-for /opt/
RUN chmod +x /opt/entrypoint.sh /opt/wait-for

WORKDIR /opt/${APP_NAME}
COPY ./${APP_NAME}/src .

ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# 'production' образ
FROM python-base as production
ARG APP_NAME

# Копируем только Python пакеты
COPY --from=builder-base /opt/venv/ /opt/venv/
ENV PATH="/opt/venv/bin:${PATH}"

COPY ./docker/${APP_NAME}/entrypoint.sh ./docker/wait-for /opt/
RUN chmod +x /opt/entrypoint.sh /opt/wait-for

RUN mkdir -p /opt/${APP_NAME}/var/log

WORKDIR /opt/${APP_NAME}
COPY ./${APP_NAME}/src .

RUN groupadd -r app && useradd -d /opt/${APP_NAME} -r -g app app \
    && chown app:app -R /opt/${APP_NAME}
USER app

ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]