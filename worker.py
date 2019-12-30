import os
import redis
from rq import Connection, Queue, Worker

# worker register
listen = ['default']

# worker url
redis_url = 'redis://redistogo:dd4b68c53cd34953a6660af0cafd6148@pike.redistogo.com:9643/'

# connection from the redis url
conn = redis.from_url(redis_url)

if __name__ == "__main__":
    with Connection(conn):
        worker = Worker(map(Queue,listen))
        worker.work()

