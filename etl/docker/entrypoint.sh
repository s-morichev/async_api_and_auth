#!/bin/bash
set -e

echo "Waiting for PostgresSQL and Elasticsearch"
/opt/wait-for postgres:5432 http://elasticsearch:9200  --timeout=0 -- echo "PostgresSQL and Elasticsearch is up"

exec "$@"