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

Переименовать env.example в .env Запустить src/manage.py

### Миграции
- Перейти в папку src `cd ./auth/src`
- Запуск контейнера постгрес без volume `docker run --env-file .env --name postgres_auth -p 5432:5432 -d postgres:15.1-alpine`
- Выполнить `flask db init` `flask db migrate` `flask db upgrade`

### Ручные проверки пост-запросов

- curl -X POST http://127.0.0.1:5000/auth/login -H "Content-Type: application/json" -d '{"email": "example", "password": "password"}'
- curl -X POST http://127.0.0.1:5000/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "email=example1&password=password"
