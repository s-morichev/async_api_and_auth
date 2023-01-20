isort:
	isort .

black:
	black -l 120 .

flake:
	flake8 --max-line-length 120 .

check_all: isort black flake

build-backend:
	docker --log-level=debug build --tag=backend --target=production -f ./backend/docker/Dockerfile  ./backend

build-etl:
	docker --log-level=debug build  --tag=etl_movies --target=production -f ./etl/docker/Dockerfile   ./etl

build-auth:
	docker --log-level=debug build --tag=auth --target=production -f ./auth/docker/Dockerfile  ./auth

build-nginx:
	docker --log-level=debug build --tag=nginx_all_services ./docker/nginx/

build-all: build-backend build-etl build-auth build-nginx

dev-run:
	docker compose up --build -d

auth-init:
	docker compose -f docker-compose.prod.yaml exec auth sh -c\
 	"flask db upgrade && flask insert-roles && flask createsuperuser --email superuser --password password"

prod-run:
	docker compose -f docker-compose.prod.yaml up -d

prod-stop:
	docker compose -f docker-compose.prod.yaml down -v


new-local-prod: build-all
	docker compose -f docker-compose.prod.yaml up -d
	docker compose -f docker-compose.prod.yaml exec auth flask db upgrade
	docker compose -f docker-compose.prod.yaml exec auth flask insert-roles
	docker compose -f docker-compose.prod.yaml exec auth flask createsuperuser --email superuser --password password

run-test-backend: build-backend
	docker compose -f docker-compose.test.yaml --env-file .env.test build test_backend
	docker compose -f docker-compose.test.yaml --env-file .env.test run --rm test_backend

run-test-auth:
	docker compose -f docker-compose.test.yaml --env-file .env.test build test_auth
	docker compose -f docker-compose.test.yaml --env-file .env.test run --rm test_auth

run-test-all: build-backend
	docker compose -f docker-compose.test.yaml --env-file .env.test build test_backend
	docker compose -f docker-compose.test.yaml --env-file .env.test build test_auth
	docker compose -f docker-compose.test.yaml --env-file .env.test run --rm test_backend
	docker compose -f docker-compose.test.yaml --env-file .env.test run --rm test_auth

stop-test:
	docker compose -f docker-compose.test.yaml --env-file .env.test down
