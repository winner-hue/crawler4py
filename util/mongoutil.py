from pymongo import MongoClient


class Mongo(object):
    __instance = None
    setting = None

    def __init__(self):
        if not Mongo.__instance:
            print("__init__ method called ....")
        else:
            print("instance already created: {}".format(self.get_instance()))

    @classmethod
    def get_instance(cls, **setting):
        if not cls.__instance:
            cls.__instance = Mongo()
            self = cls.__instance
            assert self.__init_mongo(setting.get("mongo")), "初始化mongo失败"
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
        if mongo_dup.get("user") and mongo_dup.get("pwd"):
            self.__mongo_dup = MongoClient(
                "mongodb://{}:{}@{}:{}/".format(mongo_dup.get("user"), mongo_dup.get("pwd"), mongo_dup.get("ip"),
                                                mongo_dup.get("port")), maxPoolSize=10)
        else:
            self.__mongo_dup = MongoClient(
                "mongodb://{}:{}/".format(mongo_dup.get("ip"), mongo_dup.get("port")), maxPoolSize=10)
        db_dup = self.__mongo_dup.get_database("dup") if self.__mongo_dup.get_database("dup") else self.__mongo_dup[
            "dup"]
        self.__dup = db_dup.get_collection("dup") if db_dup.get_collection("dup") else db_dup.create_collection("dup")
        return True

    def __init_mongo_monitor(self, mongo_task_monitor: dict) -> bool:
        """
        初始化任务监控库
        :param mongo_task_monitor: 任务监控库配置
        :return:
        """
        if mongo_task_monitor.get("user") and mongo_task_monitor.get("pwd"):
            self.__mongo_task_monitor = MongoClient(
                "mongodb://{}:{}@{}:{}/".format(mongo_task_monitor.get("user"), mongo_task_monitor.get("pwd"),
                                                mongo_task_monitor.get("ip"),
                                                mongo_task_monitor.get("port")), maxPoolSize=10)
        else:
            self.__mongo_task_monitor = MongoClient(
                "mongodb://{}:{}/".format(mongo_task_monitor.get("ip"), mongo_task_monitor.get("port")), maxPoolSize=10)
        self.__monitor = self.__mongo_task_monitor.get_database("monitor") if self.__mongo_task_monitor.get_database(
            "monitor") else \
            self.__mongo_task_monitor["monitor"]
        return True

    def get_params(self):
        return self.__mongo_dup, self.__mongo_task_monitor, self.__dup, self.__monitor
