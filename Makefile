isort:
	isort .

black:
	black -l 120 .

flake:
	flake8 --max-line-length 120 .

all: isort black flake

build-backend:
	docker --log-level=debug build --tag=backend_sprint_4 --target=production -f ./backend/docker/Dockerfile  ./backend

build-etl:
	docker --log-level=debug build  --tag=etl_sprint_4 --target=production -f ./etl/docker/Dockerfile   ./etl

build-db:
	docker --log-level=debug build --tag=postgres_sprint_4 ./docker/postgres/

build-nginx:
	docker --log-level=debug build --tag=nginx_sprint_4 ./docker/nginx/

build-all: build-backend build-etl build-db build-nginx

run-test: build-backend
	docker compose -f ./backend/tests/functional/docker-compose.test.yaml build test
	docker compose -f ./backend/tests/functional/docker-compose.test.yaml run --rm test

stop-test:
	docker compose -f ./backend/tests/functional/docker-compose.test.yaml down
