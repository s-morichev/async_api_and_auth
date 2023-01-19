https://github.com/RomanBorovskiy/YP_Async_API  
Участники:  
* Роман Боровский
* Сергей Моричев

### Структура разделов
/backend - бэкенд-сервис на FastAPI  
/etl - сервис ETL (копирует данные из БД в Elasticsearch)  
/docs - различная документация, касающаяся проекта  
/docker - dockefile и необходимые данные для разных сервисов, которые запускаются для работы  
/tests - Функциональные тесты для сервиса backend. Тесты для Postman  

### Запуск "development" на локальной машине
Перед этим надо переименовать `.env.example` в `.env` и указать свои пароли для сервисов  
Запуск: `docker compose up --build`

### Запуск "production" на локальной машине
Перед этим надо переименовать `.env.example` в `.env` и указать свои пароли для сервисов.
Измените в `.env` файле `BACKEND_DEBUG=False` и `AUTH_DEBUG=False`. После этого выполните
следующие команды (для проверки запуска на локальной машине можно воспользоваться `make new-local-prod`):
- Соберите образы `make build-all`
- Запустите контейнеры `docker compose -f docker-compose.prod.yaml up -d`
- При необходимости примените миграции, добавьте роли по умолчанию, создайте суперпользователя
  - `docker compose -f docker-compose.prod.yaml exec auth flask db upgrade`
  - `docker compose -f docker-compose.prod.yaml exec auth flask insert-roles`
  - `docker compose -f docker-compose.prod.yaml exec auth flask createsuperuser --email superuser --password password `


### Запуск тестов
В папке `/tests/functional/` переименуйте`.env.example` в `.env`, поменяйте пути и пароли при
необходимости. Для запуска выполните `make run-test`  
После завершения тестов тестовые контейнеры backend, elasticsearch и redis останутся запущенными,
поэтому при повторном запуске тестов не нужно будет ждать старта контейнеров. Для остановки
и удаления тестовых контейнеров выполните `make stop-test`
