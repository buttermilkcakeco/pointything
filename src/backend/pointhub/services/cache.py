from contextlib import contextmanager
import redis
import os

connection_pool = redis.ConnectionPool.from_url(os.environ['APP_DB_HOST'])

@contextmanager
def connection():
    r = redis.Redis(connection_pool=connection_pool)

    try:
        yield r
    finally:
        pass #TBD
