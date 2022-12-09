import time

from tests.functional.settings import settings
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=settings.ELK_DSN)
    while True:
        try:
            if es_client.ping():
                indices = es_client.cat.indices(h='index', s='index')
                print(', '.join(indices.split()))
                print('ES connection Ok')
                break
        except ConnectionError:
            print('wait ES for 1s...')
            time.sleep(1)
