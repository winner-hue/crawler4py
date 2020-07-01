from threading import Lock

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from log import Logger


class Mongo(object):
    __instance = None
    setting = None

    def __init__(self):
        if not Mongo.__instance:
            Logger.logger.info("开始创建mongodb实例...")
        else:
            Logger.logger.info("实例已经存在: {}".format(self.get_instance()))

    @classmethod
    def get_instance(cls, **setting):
        if not cls.__instance:
            cls.__instance = Mongo()
            self = cls.__instance
            assert self.__init_mongo(setting.get("mongo")), "初始化mongo失败"
            Logger.logger.info("Mongo创建实例成功")
        return cls.__instance

    def __init_mongo(self, mongo: dict) -> bool:
        if not mongo:
            raise Exception("mongo 配置不应为空")
        assert mongo.get("mongo_dup"), "爬虫排重库不应为空"
        assert mongo.get("mongo_task_monitor"), "爬虫任务监控库不应为空"
        mongo_dup = mongo.get("mongo_dup")
        assert self.__init_mongo_dup(mongo_dup), "初始化排重库失败"
        mongo_task_monitor = mongo.get("mongo_task_monitor")
        assert self.__init_mongo_monitor(mongo_task_monitor), "初始化任务监控库失败"
        return True

    def __init_mongo_dup(self, mongo_dup: dict) -> bool:
        """
        初始化排重库
        :param mongo_dup: 任务排重库配置
        :return:
        """
        host, port = self.get_host_port(mongo_dup)
        if mongo_dup.get("user") and mongo_dup.get("pwd"):
            __mongo_dup = MongoClient(
                "mongodb://{}:{}@{}:{}/".format(mongo_dup.get("user"), mongo_dup.get("pwd"), host, port),
                maxPoolSize=10)
        else:
            __mongo_dup = MongoClient(
                "mongodb://{}:{}/".format(host, port), maxPoolSize=10)
        db_dup = __mongo_dup.get_database("dup") if __mongo_dup.get_database("dup") else __mongo_dup[
            "dup"]
        self.__dup = db_dup.get_collection("dup") if db_dup.get_collection("dup") else db_dup.create_collection("dup")
        return True

    def __init_mongo_monitor(self, mongo_task_monitor: dict) -> bool:
        """
        初始化任务监控库
        :param mongo_task_monitor: 任务监控库配置
        :return:
        """
        host, port = self.get_host_port(mongo_task_monitor)
        if mongo_task_monitor.get("user") and mongo_task_monitor.get("pwd"):
            __mongo_task_monitor = MongoClient(
                "mongodb://{}:{}@{}:{}/".format(mongo_task_monitor.get("user"), mongo_task_monitor.get("pwd"),
                                                host, port), maxPoolSize=10)
        else:
            __mongo_task_monitor = MongoClient("mongodb://{}:{}/".format(host, port), maxPoolSize=10)
        self.__monitor = __mongo_task_monitor.get_database("monitor") if __mongo_task_monitor.get_database(
            "monitor") else \
            __mongo_task_monitor["monitor"]
        return True

    def get_params(self):
        return self.__dup, self.__monitor

    @staticmethod
    def get_host_port(obj: dict):
        host = obj.get("host") if obj.get("host") else "127.0.0.1"
        port = obj.get("port") if obj.get("port") else 27017
        return host, port


class MongoUtil(object):
    __instance = None
    dup: Collection
    monitor: Database
    lock = Lock()

    def __init__(self):
        if not MongoUtil.__instance:
            Logger.logger.info("开始创建MongoUtil实例")
        else:
            Logger.logger.info("MongoUtil实例已经存在，{}".format(self.get_instance()))

    @classmethod
    def get_instance(cls, **setting):
        if MongoUtil.__instance:
            return MongoUtil.__instance

        with MongoUtil.lock:
            if not cls.__instance:
                cls.__instance = MongoUtil()
                cls.dup, cls.monitor = Mongo.get_instance(**setting).get_params()
                Logger.logger.info("MongoUtil实例创建成功")
            return cls.__instance

    @classmethod
    def insert_one(cls, params: dict):
        cls.dup.insert_one(params)
