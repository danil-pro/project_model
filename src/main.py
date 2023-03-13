# import redis
# import time
# import json
# import json

import aiohttp
import requests
import config
import asyncio
from Worker import RedisUsers

url = config.URL
data = config.DATA
worker_name = config.WORKER_NAME
search_mode = config.SEARCH_MODE

lyft_url = "https://api.lyft.com/v1/driver-mode"

users_dict = RedisUsers(url, data, worker_name, search_mode).get_users()
print(len(users_dict))


async def make_request(headers, session):
    response = await session.get(lyft_url, headers=headers, data={}, ssl=False)
    return response


async def get_users(queue, session, user):
    headers = {'Authorization': f"{user.get('token_type')} {user.get('access_token')}"}
    response = await make_request(headers, session)
    await queue.put(await response.text())


async def main():
    # users = await asyncio.create_task(get_users())
    session = aiohttp.ClientSession()
    users_queue = asyncio.Queue()

    task = [asyncio.create_task(
        get_users(users_queue, session, user))for user in users_dict.values()]

    await asyncio.gather(*task)

    print(users_queue)

    await session.close()

asyncio.run(main())
