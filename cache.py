import redis
import os
from pickle import dumps, loads

CACHE_SERVER = [os.getenv('REDIS_HOST'), os.getenv('REDIS_PORT'),
                os.getenv('REDIS_PASSWORD', "redis-666")]

CACHE_TMP = CACHE_SERVER + [1, 'tmp']
CACHE_STATIC = CACHE_SERVER + [2, 'static']
CACHE_API = CACHE_SERVER + [3, 'api']
CACHE_ACCOUNT = CACHE_SERVER + [4, 'account']
CACHE_TEMP = CACHE_SERVER + [0, 'temp']
CONNECTIONS = {}


def get_connection(config):
    global CONNECTIONS
    if config[4] not in CONNECTIONS:
        pool = redis.ConnectionPool(host=config[0], port=config[1], password=config[2], db=config[3])
        connection = CONNECTIONS[config[4]] = redis.Redis(connection_pool=pool)
    else:
        connection = CONNECTIONS[config[4]]
    return connection


class Cache(object):

    def __init__(self, config=CACHE_TMP):
        """
        @note:  use persistent connection
        """
        self.conn = get_connection(config)

    def get(self, key, original=False):
        """
        @note: original  stands for if store the origin value or not，when using incr
        """
        obj = self.conn.get(key)
        if obj:
            return loads(obj) if not original else obj
        return None

    def set(self, key, value, time_out=0, original=False):
        s_value = dumps(value) if not original else value
        time_out = int(time_out)
        if time_out:
            if self.conn.exists(key):
                self.conn.setex(name=key, value=s_value, time=time_out)
            else:
                self.conn.setnx(name=key, value=s_value)
                self.conn.expire(name=key, time=time_out)
        else:
            self.conn.set(name=key, value=s_value)

    def delete(self, key):
        return self.conn.delete(key)

    def incr(self, key, delta=1):
        return self.conn.incrby(key, delta)

    def decr(self, key, delta=1):
        return self.conn.decr(key, delta)

    def exists(self, key):
        return self.conn.exists(key)

    def llen(self, key):
        return self.conn.llen(key)

    def ttl(self, key):
        return self.conn.ttl(key)

    def get_time_is_locked(self, key, time_out):
        '''
        @note: set lock time
        '''
        key = "tlock_%s" % key
        if self.conn.exists(key):
            return True

        # self.conn.setex(key, '0', time_out)
        self.set(key, 0, time_out)
        return False

    def set_lock(self, key, value, ex=None, px=None, nx=False, xx=False):
        return self.conn.set(key, dumps(value), ex, px, nx, xx)

    def flush(self):
        self.conn.flushdb()


class CacheQueue(Cache):
    """
    @note: a fixed queue used redis list type
    """

    def __init__(self, key, max_len, config, time_out=0):
        self.key = "queue_%s" % key
        self.max_len = max_len
        self.time_out = time_out
        self.conn = get_connection(config)

    def push(self, item):
        if self.conn.llen(self.key) < self.max_len:
            self.conn.lpush(self.key, item)
        else:
            def _push(pipe):
                pipe.multi()
                pipe.rpop(self.key)
                pipe.lpush(self.key, item)

            self.conn.transaction(_push, self.key)
        if self.time_out:
            self.conn.expire(self.key, self.time_out)

    def pop(self, value, num=0):
        self.conn.lrem(self.key, value, num)

    def init(self, items):
        '''
        @note: init a list
        '''
        self.delete()
        if items:
            self.conn.rpush(self.key, *items)

    def delete(self):
        self.conn.delete(self.key)

    def exists(self):
        return self.conn.exists(self.key)

    def __getslice__(self, start, end):
        if not self.conn.exists(self.key):
            return None
        return self.conn.lrange(self.key, start, end)


def get_or_update_data_from_cache(_key, _expire, _cache_config, _must_update_cache, _func, *args, **kwargs):
    """
    @note: automatically saved the result of the func
    data cannot be null for the first time, we use the val to check if it has been cached or not
    :param _key:
    :param _expire:
    :param _cache_config:
    :param _must_update_cache:
    :param _func:
    :param args:
    :param kwargs:
    :return:
    """
    cache_obj = Cache(config=_cache_config)
    data = cache_obj.get(_key)
    if data is None or _must_update_cache:
        data = _func(*args, **kwargs)
        if data is not None:
            cache_obj.set(_key, data, time_out=_expire)
    return data


if __name__ == '__main__':
    cache_obj = Cache()
