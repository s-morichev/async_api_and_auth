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

!! Pytest или Flask при тестировании по умолчанию загружают переменные окружения из .env файла,
поэтому нужно удалить/переименовать .env файл в корневой папке проекта, иначе загрузятся неправильные переменные

- Перейти в папку auth `cd ./auth`
- Переименовать env.local.example в .env.local `cp .env.local.example .env.local`
- Запустить контейнеры postgres и redis при необходимости `make run-db`
- Применить миграции `make upgrade` (если миграций нет - то создать и применить `make init`)
- Запустить сервис `make run`
- По завершении работы удалить контейнеры `make stop-db` (контейнеры без volume - все данные удалятся)

Для создания новой миграции `make migrate msg='migration description here`

### Тесты

- Переименовать env.test.example в .env.test `cp .env.test.example .env.test`
- Запустить контейнеры для тестов `make run-test-db`
- Запустить тесты `make test`
- По завершении тестирования удалить контейнеры `make stop-test-db`
