#!/bin/bash
set -e

echo "Waiting for PosgreSQL and Elasticsearch"
/opt/wait-for postgres:5432 http://elasticsearch:9200  --timeout=0 -- echo "PosgreSQL and Elasticsearch is up"

exec "$@"