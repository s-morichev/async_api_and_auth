#!/bin/bash
set -e

echo "Waiting for PostgresSQL and Elasticsearch"
/opt/wait-for postgres_movies:5432 http://elasticsearch_movies:9200  --timeout=0 -- echo "PostgresSQL and Elasticsearch is up"

exec "$@"