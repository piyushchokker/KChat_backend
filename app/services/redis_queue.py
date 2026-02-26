import redis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = "file_queue"

r = redis.Redis.from_url(REDIS_URL)

def add_to_queue(metadata: dict):
    r.rpush(QUEUE_NAME, json.dumps(metadata))

def pop_from_queue():
    item = r.lpop(QUEUE_NAME)
    if item:
        return json.loads(item)
    return None

def get_queue_length():
    return r.llen(QUEUE_NAME)

def peek_queue():
    item = r.lindex(QUEUE_NAME, 0)
    if item:
        return json.loads(item)
    return None
