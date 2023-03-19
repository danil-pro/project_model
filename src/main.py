# import redis
# import time
# import json
# import json
import json
# from concurrent.futures import ProcessPoolExecutor

import aiohttp
# import requests
import config
import asyncio
from Worker import Worker

url = config.URL
data = config.DATA
worker_name = config.WORKER_NAME
search_mode = config.SEARCH_MODE


# lyft_url_driver_mode = "https://api.lyft.com/v1/driver-mode"
# lyft_url_location = 'https://api.lyft.com/v1/locations'

# print(json.dumps(users_dict, indent=4))
# print(len(users_dict))


async def make_response(headers, session, user, lyft_url, payload):
    response = await session.get(lyft_url, headers=headers, data=payload, ssl=False)
    return response, user.get('key')


async def get_user_location(headers, session, lyft_url, payload):
    response = await session.post(lyft_url, headers=headers, data=payload, ssl=False)
    return response


async def get_users(users_queue, session, user):
    lyft_url = "https://api.lyft.com/v1/driver-mode"
    payload = {}
    headers = {'Authorization': f"{user.get('token_type')} {user.get('access_token')}"}
    # print(headers)
    response = await make_response(headers, session, user, lyft_url, payload)
    await users_queue.put([await response[0].text(), response[0].status, response[-1]])


async def get_online_users(users_queue, offline_users_queue, user):
    while True:
        await asyncio.sleep(0)
        response = await users_queue.get()
        # print(response[0])
        if response[1] == 200:
            user_json = json.loads(response[0])
            driver_mode = user_json.get('driver_mode')
            online = driver_mode.get('online')
            if not online and user != 'log':
                await offline_users_queue.put(user)

        elif response[1] == 401:
            print(response)
        elif response[1] == 503:
            print(response[-1])

        users_queue.task_done()


async def offline_users(user_location_queue, offline_users_queue, session, users_dict):
    while True:
        users = await offline_users_queue.get()
        print(users)
        lyft_url = 'https://api.lyft.com/v1/locations'
        payload = users_dict.get(users)
        headers = {'Authorization': f"{payload.get('token_type')} {payload.get('access_token')}"}
        location = await get_user_location(headers, session, lyft_url, json.dumps(payload))

        await user_location_queue.put(await location.text())

        offline_users_queue.task_done()


async def main():
    users_dict = Worker(url, data, worker_name, search_mode).get_users()
    print(len(users_dict))
    # users = await asyncio.create_task(get_users())
    session = aiohttp.ClientSession()
    users_queue = asyncio.Queue()
    offline_users_queue = asyncio.Queue()
    user_location_queue = asyncio.Queue()

    users_getters = [asyncio.create_task(
        get_users(users_queue, session, user)) for user in users_dict.values()]

    users_online_getters = [asyncio.create_task(
        get_online_users(users_queue, offline_users_queue, user)) for user in list(users_dict)]

    user_location_getters = [asyncio.create_task(
        offline_users(user_location_queue, offline_users_queue, session, users_dict))]

    await asyncio.gather(*users_getters)

    await offline_users_queue.join()
    for task in users_online_getters:
        task.cancel()

    print(user_location_queue)

    await session.close()


asyncio.run(main())
