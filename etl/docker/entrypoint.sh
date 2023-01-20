#!/bin/bash
set -e

echo "Waiting for PostgresSQL and Elasticsearch"
python3 /opt/wait_for_services.py

exec "$@"