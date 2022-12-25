#!/bin/bash
set -e

echo "Waiting for Postgres and Redis"
/opt/wait-for postgres_auth:5432 --timeout=0 -- echo "Postgres is up"
/opt/wait-for redis_auth:6379 --timeout=0 -- echo "Redis is up"

exec "$@"