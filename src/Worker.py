import redis
import time
import json


class Worker:
    def __init__(self, url, data, worker_name, search_mode):
        self.redis = redis.from_url(url)
        self.data = data
        self.worker_name = worker_name
        self.search_mode = search_mode

    def get_users(self):
        hash_data = self.redis.get(self.data).decode()
        keys_data = [self.worker_name, self.search_mode, int(time.time_ns() / 1000000), 1]
        users = self.redis.evalsha(hash_data, 1, *keys_data)
        return json.loads(users)
