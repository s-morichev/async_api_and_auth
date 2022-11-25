#!/bin/bash
set -e

echo "Waiting for Elasticsearch"
/opt/wait-for http://elasticsearch:9200  --timeout=0 -- echo "Elasticsearch is up"

exec "$@"