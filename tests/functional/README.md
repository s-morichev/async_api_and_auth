Тесты для бэкенда в папке /backend/tests, чтобы разделить тестирование backend и etl, 
и еще делаем папку /backend примерно как отдельный репозиторий

В начале сессии автоматически создаются клиент эластика и индексы в эластике. В тестах
доступны фикстуры es_write_data и make_get_request. Предполагается, что в начале каждого
теста в эластик загружаем тестовые данные, потом делаем запрос и сравниваем 
полученные данные с правильным ответом.

К фикстуре es_write_data добавлен finalizer, который автоматически удаляет все документы из
всех индексов эластика. То есть, если тесте загрузили данные с помощью es_write_data,
то в конце теста все индексы останутся пустыми.

После завершения всех тестов автоматически удаляются сами индексы, то эластик после
всех тестов возвращается к исходному пустому состоянию, как будто сразу после запуска
нового контейнера.

Тесты можно запускать локально командой pytest при поднятых контейнерах бэкенда, 
эластика и редиса на локалхосте.