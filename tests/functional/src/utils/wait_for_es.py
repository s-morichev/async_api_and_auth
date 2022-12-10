import time

from elasticsearch import Elasticsearch

from functional.src.settings import settings

if __name__ == "__main__":
    es_client = Elasticsearch(settings.ES_URI)
    while True:
        if es_client.ping():
            break
        print("wait es, sleep 1s")
        time.sleep(1)
