import asyncio
import time

import aiohttp

from settings import settings


async def wait():
    # TODO посмотреть как лучше пинговать сервис
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(settings.API_URI):
                    break
            except aiohttp.ClientConnectionError:
                print("wait backend, sleep 1s")
                time.sleep(1)


if __name__ == "__main__":
    asyncio.run(wait())
