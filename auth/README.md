### Структура /src

- /app - непосредственно приложение
  - \_\_init__.py - application factory
  - /models - модели
  - /services - бизнес-логика
  - /views - ендпойнты
  - /db - модули с абстракциями для базы данных и редис
  - /core - общие модули
  
- /migrations - миграции alembic
- config.py - конфигурация Flask
- manage.py - создание экземпляра приложения, консольные команды

### Локальный запуск

- Перейти в папку auth `cd ./auth`
- Переименовать env.local.example в .env.local `cp .env.local.example .env.local`
- Зпустить контейнеры при необходимости
  - постгрес без volume `docker run --env-file .env --name postgres_auth -p 5432:5432 -d postgres:15.1-alpine`
  - редис без volume `docker run --name redis_auth -p 6379:6379 -d redis:7.0.5-alpine`
- перейти в папку src `cd ./src`
  
- инициализация БД:  `make init` - !!!!! НЕ РАБОТАЕТ !!!!!
- запуск: `make run`


### Тесты

Локальный запуск тестов
Контейнеры (номер порта на 20000 больше, чтобы не было конфликта с не тестовыми контейнерами)
- `docker run --env POSTGRES_USER=app --env POSTGRES_PASSWORD=123qwe --env POSTGRES_DB=test_users_database --name postgres_auth_test -p 25432:5432 -d postgres:15.1-alpine`
- `docker run --name redis_auth_test -p 26379:6379 -d redis:7.0.5-alpine`

Выполнение тестов `pytest auth` из корневой папки
