https://github.com/RomanBorovskiy/YP_Async_API  
Участники:  
* Роман Боровский
* Сергей Моричев

### Структура разделов
/backend - сервис на FastAPI  
/etl - сервис ETL (копирует данные из БД в Elasticsearch)  
/docs - различная документация, касающаяся проекта  
/docker - dockefile и необходимые данные для разных сервисов, которые запускаются для работы  
/tests - тесты для сервиса backend. Коллекция для Postman  

### Запуск "development" на локальной машине
Запуск: docker compose up --build  
Перед этим надо переименовать .env.example в .env и указать свои пароли для сервисов


### Запуск "production" на локальной машине

Измените в .env файле `BACKEND_DEBUG=False`. После этого выполните следующие команды:

- Соберите образы `make build-all`
- Запустите контейнеры `docker compose -f docker-compose.prod.yaml up -d`
