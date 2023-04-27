### API онлайн кинотеатра (бэкенд и авторизация)

Сервисы предоставляют API для получения информации о фильмах и API для
регистрации и авторизации пользователелй.

### Над проектом работали:  
* Роман Боровский https://github.com/RomanBorovskiy
* Сергей Моричев https://github.com/s-morichev

### Структура разделов
/auth - сервис аутентификации и авторизации
/backend - бэкенд-сервис на FastAPI  
/etl - сервис ETL (копирует данные из БД в Elasticsearch)  
/docker - dockefile и необходимые данные для разных сервисов, которые запускаются для работы  
/docs - различная документация, касающаяся проекта  
/tests - Функциональные тесты для сервиса backend. Тесты для Postman  

### Запуск "development" на локальной машине
Перед этим надо переименовать `.env.example` в `.env` и указать свои пароли для сервисов  
Запуск: `make dev-run` (или `docker compose up --build`)

### Запуск "production" на локальной машине
Перед этим надо переименовать `.env.example` в `.env` и указать свои пароли для сервисов.
Измените в `.env` файле `BACKEND_DEBUG=False` и `AUTH_DEBUG=False`. После этого выполните
следующие команды (для проверки запуска на локальной машине можно воспользоваться `make new-local-prod`):
- Соберите образы `make build-all`
- Запустите контейнеры `make prod-run` (или `docker compose -f docker-compose.prod.yaml up -d`)

- При необходимости примените миграции, добавьте роли по умолчанию, создайте суперпользователя:
  `make auth-init`, что равносильно командам:
  - `docker compose -f docker-compose.prod.yaml exec auth flask db upgrade`
  - `docker compose -f docker-compose.prod.yaml exec auth flask insert-roles`
  - `docker compose -f docker-compose.prod.yaml exec auth flask createsuperuser --email superuser --password password`

Для оcтановки и удаления контейнеров выполните `make prod-stop` (или `docker compose -f docker-compose.prod.yaml down -v`)

Jaeger UI доступен по адресу http://127.0.0.1:16686/


### Запуск тестов
В корневой папке переименуйте`.env.test.example` в `.env.test`, поменяйте пути и пароли при
необходимости. Для запуска выполните `make run-test-all`
Запуск тестов только сервиса auth - `make run-test-auth`  
Запуск тестов только сервиса backend - `make run-test-backend`
После завершения тестов тестовые контейнеры backend, elasticsearch, redis и postgres
останутся запущенными, поэтому при повторном запуске тестов не нужно будет ждать старта
контейнеров. Для остановки и удаления тестовых контейнеров выполните `make stop-test`
