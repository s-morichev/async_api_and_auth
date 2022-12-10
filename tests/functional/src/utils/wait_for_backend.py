import time
from http.client import HTTPConnection

from functional.src.settings import settings

if __name__ == "__main__":
    cut_off = len("http://")
    connection = HTTPConnection(settings.API_URI[cut_off:])
    while True:
        try:
            connection.connect()
            break
        except ConnectionRefusedError:
            print("wait backend, sleep 1s")
            time.sleep(1)
