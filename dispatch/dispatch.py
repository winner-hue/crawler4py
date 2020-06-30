from threading import Thread

from log import Logger
from pycrawler import Crawler
from util.mongoutil import MongoUtil
from util.running_params import task_q
from util.sqlutil import SqlUtil


class Dispatch(Crawler):

    def __init__(self, **setting):
        super(Dispatch, self).__init__(**setting)
        self.dispatch = []
        self.downloader = []
        self.extractor = []
        self.storage_dup = []

    def start(self):
        for index, dispatch in enumerate(self.dispatch):
            Thread(target=dispatch.run, name=f"dispatch--{index}").start()

        for index, downloader in enumerate(self.downloader):
            Thread(target=downloader.run, name=f"downloader--{index}").start()

        for index, extractor in enumerate(self.extractor):
            Thread(target=extractor.run, name=f"extractor--{index}").start()

        for index, storage_dup in enumerate(self.storage_dup):
            Thread(target=storage_dup.run, name=f"storage-dup--{index}").start()

    def run(self):
        Logger.logger.info("dispatch 开始启动")
        try:
            Thread(target=self.process).start()
            Logger.logger.info("dispatch 启动成功")
        except Exception as e:
            Logger.logger.info("dispatch 启动失败：{}".format(e))

    def process(self):
        if task_q.empty():
            try:
                MongoUtil.get_instance(**self.crawler_setting)
                SqlUtil.get_instance(**self.crawler_setting.get("sql"))
            except:
                raise Exception("数据库初始化失败， 请检查配置文件")
            MongoUtil.dup.insert_one({"user": "name"})
            tasks = self.get_tasks()

    def get_tasks(self) -> list:
        pass
