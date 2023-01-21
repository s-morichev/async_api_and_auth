init:
	sh -c "export FLASK_APP='./src/manage.py' && flask db init && flask db migrate && flask db upgrade"
	#sh -c "export FLASK_APP='./src/manage.py' && flask db migrate && flask db upgrade"

run:
	python ./src/manage.py

test:
	docker run --env POSTGRES_USER=app --env POSTGRES_PASSWORD=123qwe --env POSTGRES_DB=test_users_database --name postgres_auth_test -p 25432:5432 -d postgres:15.1-alpine
	docker run --name redis_auth_test -p 26379:6379 -d redis:7.0.5-alpine
	pytest ./tests

