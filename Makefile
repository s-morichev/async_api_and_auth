isort:
	isort .

black:
	black -l 120 .

flake:
	flake8 --max-line-length 120 .

all: isort black flake

build-backend:
	docker --log-level=debug build --tag=backend --target=production -f ./backend/docker/Dockerfile  ./backend

build-etl:
	docker --log-level=debug build  --tag=etl_movies --target=production -f ./etl/docker/Dockerfile   ./etl

build-auth:
	docker --log-level=debug build --tag=auth --target=production -f ./auth/docker/Dockerfile  ./auth

build-nginx:
	docker --log-level=debug build --tag=nginx_all_services ./docker/nginx/

build-all: build-backend build-etl build-auth build-nginx

new-local-prod: build-all
	docker compose -f docker-compose.prod.yaml up -d
	docker compose -f docker-compose.prod.yaml exec auth flask db upgrade
	docker compose -f docker-compose.prod.yaml exec auth flask insert-roles
	docker compose -f docker-compose.prod.yaml exec auth flask createsuperuser --email superuser --password password

run-test: build-backend
	docker compose -f ./tests/functional/docker-compose.test.yaml build test
	docker compose -f ./tests/functional/docker-compose.test.yaml run --rm test

stop-test:
	docker compose -f ./tests/functional/docker-compose.test.yaml down
