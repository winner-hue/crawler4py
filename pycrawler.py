from util.mongoutil import Mongo


class Crawler(object):
    def __init__(self, **setting: dict):
        if not setting:
            raise Exception("配置属性setting不能为空")
        self.crawler_mode = setting.get("crawler_mode")
        self.mongo_dup, self.mongo_task_monitor, self.dup, self.monitor = Mongo.get_instance(**setting).get_params()
        self.switch = True  # 任务启动开关
        self.start_url = None  # 初始任务url
        self.dispatch = []
        self.downloader = []
        self.extractor = []
        self.storage_dup = []

    def installed(self, obj, obj_type):
        if obj_type == 1:
            self.dispatch.append(obj)
        if obj_type == 2:
            self.downloader.append(obj)
        if obj_type == 3:
            self.extractor.append(obj)
        if obj_type == 4:
            self.storage_dup.append(obj)

    def run(self):
        raise NotImplemented
