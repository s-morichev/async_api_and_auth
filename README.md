https://github.com/RomanBorovskiy/YP_Async_API  
Участники:  
* Роман Боровский
* Сергей Моричев


Запуск "production" на локальной машине

Измените в .env файле `BACKEND_DEBUG=False`. После этого выполните следующие команды:

- Соберите образы `make build-all`
- Запустите контейнеры `docker compose -f docker-compose.prod.yaml up -d`