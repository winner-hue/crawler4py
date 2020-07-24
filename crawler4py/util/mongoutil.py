from threading import Lock

from pymongo import MongoClient
from pymongo.collection import Collection

from crawler4py.log import Logger


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
        mongo = mongo.get("database")
        host, port = self.get_host_port(mongo)
        if mongo.get("user") and mongo.get("pwd"):
            __mongo = MongoClient(
                "mongodb://{}:{}@{}:{}/".format(mongo.get("user"), mongo.get("pwd"), host, port),
                maxPoolSize=10)
        else:
            __mongo = MongoClient(
                "mongodb://{}:{}/".format(host, port), maxPoolSize=10)
        db = __mongo.get_database("databases") if __mongo.get_database("databases") else __mongo[
            "databases"]
        collection_name = mongo.get("collection_name")
        self.collection = db.get_collection(collection_name) if db.get_collection(
            collection_name) else db.create_collection(collection_name if collection_name else "database")
        return True

    def get_params(self):
        return self.collection

    @staticmethod
    def get_host_port(obj: dict):
        host = obj.get("host") if obj.get("host") else "127.0.0.1"
        port = obj.get("port") if obj.get("port") else 27017
        return host, port


class MongoUtil(object):
    __instance = None
    collection: Collection
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
                cls.collection = Mongo.get_instance(**setting).get_params()
                Logger.logger.info("MongoUtil实例创建成功")
            return cls.__instance

    @classmethod
    def insert_one(cls, params: dict):
        cls.collection.insert_one(params)
