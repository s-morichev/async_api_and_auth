#!/bin/bash
set -e

echo "Waiting for Elasticsearch and Redis"
/opt/wait-for http://elasticsearch:9200 --timeout=0 -- echo "Elasticsearch is up"
/opt/wait-for redis:6379 --timeout=0 -- echo "Redis is up"

exec "$@"