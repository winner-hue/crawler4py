from threading import Lock

import redis
from redis import Redis as RedisClient

from crawler4py.log import Logger


class Redis(object):
    __instance = None
    setting = None

    def __init__(self):
        if not Redis.__instance:
            Logger.logger.info("开始创建redis实例...")
        else:
            Logger.logger.info("redis实例已经存在: {}".format(self.get_instance()))

    @classmethod
    def get_instance(cls, **setting):
        if not cls.__instance:
            cls.__instance = Redis()
            cls.__instance.__init_redis(setting.get("redis"))
            Logger.logger.info("redis创建实例成功")
        return cls.__instance

    def __init_redis(self, redis_config: dict):
        if not redis_config:
            raise Exception("redis 配置不应为空")
        assert redis_config.get("dup"), "爬虫排重库不应为空"
        assert redis_config.get("task_monitor"), "爬虫任务监控库不应为空"
        self.__init_redis_dup(redis_config.get("dup"))
        self.__init_redis_monitor(redis_config.get("task_monitor"))

        if redis_config.get("dup").get("bloomfilter"):
            self.__init_bloom_filter(redis_config.get("dup"))

    def __init_redis_dup(self, redis_dup: dict):
        """
        初始化排重库
        :param redis_dup: 任务排重库配置
        :return:
        """
        host, port, db = self.get_redis_params(redis_dup)
        if redis_dup.get("pwd"):
            pool = redis.ConnectionPool(host=host, port=port, db=db, password=redis_dup.get("pwd"))
        else:
            pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.dup = RedisClient(connection_pool=pool)

    def __init_redis_monitor(self, redis_task_monitor: dict):
        """
        初始化任务监控库
        :param redis_task_monitor: 任务监控库配置
        :return:
        """
        host, port, db = self.get_redis_params(redis_task_monitor)
        if redis_task_monitor.get("pwd"):
            pool = redis.ConnectionPool(host=host, port=port, db=db, password=redis_task_monitor.get("pwd"))
        else:
            pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.monitor = RedisClient(connection_pool=pool)
        self.expire = redis_task_monitor.get("expire") if redis_task_monitor.get("expire") else 10 * 60

    def __init_bloom_filter(self, bloom):
        block_num = bloom.get("blocknum") if bloom.get("blocknum") else 1
        key = 'dup'
        self.bit_size = 1 << 31  # Redis的String类型最大容量为512M，现使用256M
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.key = key
        self.block_num = block_num
        self.hash_func = []
        for seed in self.seeds:
            self.hash_func.append((self.bit_size, seed))

    @staticmethod
    def get_redis_params(obj: dict):
        host = obj.get("host") if obj.get("host") else "127.0.0.1"
        port = obj.get("port") if obj.get("port") else 6379
        db = obj.get("db") if obj.get("db") else 0
        return host, port, db


class RedisUtil(object):
    __instance = None
    lock = Lock()
    dup: RedisClient = None
    monitor: RedisClient = None
    hash_func = None
    block_num = None
    key = None
    expire = None

    def __init__(self):
        if not RedisUtil.__instance:
            Logger.logger.info("开始创建RedisUtil实例")
        else:
            Logger.logger.info("RedisUtil实例已经存在，{}".format(self.get_instance()))

    @classmethod
    def get_instance(cls, **setting):
        if RedisUtil.__instance:
            return RedisUtil.__instance

        with RedisUtil.lock:
            if not cls.__instance:
                cls.__instance = RedisUtil()
                __redis = Redis.get_instance(**setting)
                cls.dup = __redis.dup
                cls.monitor = __redis.monitor
                try:
                    cls.hash_func = __redis.hash_func
                    cls.block_num = __redis.block_num
                    cls.key = __redis.key
                except AttributeError:
                    pass
                cls.expire = __redis.expire
                Logger.logger.info("RedisUtil实例创建成功")
            return RedisUtil.__instance

    @staticmethod
    def hash(value, cap, seed):
        ret = 0
        for i in range(len(value)):
            ret += seed * ret + ord(value[i])
        return (cap - 1) & ret

    @classmethod
    def is_contains(cls, key):
        """
        排重
        :param key:
        :return:
        """
        ret = True
        if cls.hash_func:
            name = key + str(int(key[0:2], 16) % cls.block_num)
            for f in cls.hash_func:
                loc = cls.hash(key, f[0], f[1])
                ret = ret & RedisUtil.dup.getbit(name, loc)
                if not ret:
                    return False
        else:
            ret = True if cls.dup.sismember("dup", key) else False
        return ret

    @classmethod
    def insert(cls, key):
        if cls.hash_func:
            name = cls.key + str(int(key[0:2], 16) % cls.block_num)
            for f in cls.hash_func:
                loc = cls.hash(key, f[0], f[1])
                RedisUtil.dup.setbit(name, loc, 1)
        else:
            RedisUtil.dup.sadd("dup", key)

    @classmethod
    def get_lock(cls):
        result = True
        if cls.dup.get("lock"):
            result = False
        else:
            cls.dup.set("lock", "lock")
        return result

    @classmethod
    def release_lock(cls):
        return cls.dup.delete("lock")

    @classmethod
    def monitor_task(cls, key):
        pipeline = cls.monitor.pipeline()
        pipeline.zadd(key, {key: 100})
        pipeline.expire(key, cls.expire)
        pipeline.execute()

    @classmethod
    def release_monitor(cls, key):
        cls.monitor.delete(key)

    @classmethod
    def monitor_insert(cls, key, score, value):
        """
        临时任务插入数据
        :param key:
        :param score:
        :param value:
        :return:
        """
        ttl = cls.monitor.ttl(key)
        if ttl > 0:
            return cls.monitor.zadd(key, {value: score})
        else:
            return False

    @classmethod
    def is_exist(cls, key, value):
        return cls.monitor.zscore(key, value)

    @classmethod
    def del_exist(cls, key, value):
        return cls.monitor.zrem(key, value)

    @classmethod
    def monitor_is_exist(cls, key):
        """
        判断临时任务库是否存在
        :param key:
        :return:
        """
        ttl = cls.monitor.ttl(key)
        if ttl > 0:
            return True
        else:
            return False

    @classmethod
    def monitor_ttl(cls, key):
        return cls.monitor.ttl(key)

    @classmethod
    def monitor_score(cls, key):
        return cls.monitor.zcount(key, 10, 10)
