# Исходный контейнер
FROM python:3.10.8-slim

# папка, в которой будут размещаться файлы проекта внутри контейнера
WORKDIR /app

# отключение буферизации вывода (output)
ENV PYTHONUNBUFFERED 1
# Python не будет пытаться создавать файлы .pyc
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt requirements.txt
# Ставим зависимости
# --no-cache-dir -  отключаем кэширование pip
RUN   pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# копируем что надо в контейнер
#COPY ./etc ./etc
MKDIR ./var
COPY ./src ./src

ENTRYPOINT ["python","./src/main.py"]