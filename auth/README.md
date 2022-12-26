### Структура src

- /app - непосредственно приложение
  - __init__.py - application factory
  - /models - модели
  - /services - бизнес-логика
  - /views - ендпойнты, наверно лучше перенести их в api/v1, по крайней мере круды по ролям
- /migrations - миграции alembic
- config.py - конфигурация Flask
- manage.py - создание экземпляра приложения, консольные команды

### Локальный запуск

- Перейти в папку auth `cd ./auth`
- Переименовать env.example в .env `cp .env,example .env`
- Зпустить контейнеры при необходимости
  - постгрес без volume `docker run --env-file .env --name postgres_auth -p 5432:5432 -d postgres:15.1-alpine`
  - редис без volume `docker run --name redis_auth -p 6379:6379 -d redis:7.0.5-alpine`
- перейти в папку src `cd ./src`
- экспортировать `export FLASK_APP='manage.py'` для более удобного запуска консольных команд
- создать и применить миграции `flask db init` `flask db migrate` `flask db upgrade`
- создать роли и несколько юзеров для примера `flask insert-roles` `flask insert-users`
- запустить manage.py

### Ручные проверки пост-запросов

- http :5000/auth/register email=example password=password
- http :5000/auth/login email=example1 password=password
- http :5000/auth/me Authorization:"Bearer $ACCESS_TOKEN"
- http :5000/auth/refresh Authorization:"Bearer $REFRESH_TOKEN"
