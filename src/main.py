import asyncio
import redis
from sqlalchemy import create_engine
import config

url = config.URL


async def coro():
    return 'hello world'


async def main():
    a = await asyncio.create_task(coro())
    print(a)

asyncio.run(main())
