import os
import json
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = "file_queue"

r = redis.from_url(REDIS_URL, decode_responses=True)


async def add_to_queue(metadata: dict):
    await r.rpush(QUEUE_NAME, json.dumps(metadata))

# async def blpeek():
#     _, item = await r.blpop(QUEUE_NAME)  # blocks efficiently
#     await r.lpush(QUEUE_NAME, item)      # push it back immediately
#     return json.loads(item)


async def pop_from_queue():
    item = await r.blpop(QUEUE_NAME)
    if item:
        _, value = item
        return json.loads(value)
    return None


async def get_queue_length():
    return await r.llen(QUEUE_NAME)


async def peek_queue():
    item = await r.lindex(QUEUE_NAME, 0)
    if item:
        return json.loads(item)
    return None


async def close_redis():
    await r.close()