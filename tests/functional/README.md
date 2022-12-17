/testdata схемы индексов эластика и тестовые сгенерированные наборы данных  
/tests тесты pytest  
/utils вспомогательные модули  

запуск локально:
`.env.local.example` переименовать в `env.local` и поменять пути на правильные  
выполнить: `pytest .` 

запуск в докере:
docker compose -f docker-compose.test.yaml up