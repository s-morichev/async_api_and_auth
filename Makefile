isort:
	isort .

black:
	black -l 120 .

flake:
	flake8 --max-line-length 120 .

all: isort black flake

build-backend:
	docker --log-level=debug build --file=docker/backend/Dockerfile --tag=backend_sprint_4 --target=production .

build-etl:
	docker --log-level=debug build --file=docker/etl/Dockerfile --tag=etl_sprint_4 --target=production .

build-db:
	docker --log-level=debug build --tag=postgres_sprint_4 ./docker/postgres/

build-nginx:
	docker --log-level=debug build --tag=nginx_sprint_3 ./docker/nginx/

build-all: build-backend build-etl build-db build-nginx