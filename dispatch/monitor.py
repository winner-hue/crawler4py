import re
import threading
import time

from dispatch.dispatch import Dispatch
from download.downloader import Downloader
from extractor.extractor import Extractor
from log import Logger
from pycrawler import Crawler
from storage_dup import BaseStorageDup
from util.mongoutil import MongoUtil


class Monitor(object):
    __instance = None

    def __init__(self):
        if Monitor.__instance:
            Logger.logger.info("monitor已经初始化")
        else:
            Logger.logger.info("monitor开始初始化")

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = Monitor()
            Logger.logger.info("monitor初始化成功")
        return cls.__instance

    @staticmethod
    def thread_monitor(*args):
        """
        线程监控
        :param args:
        :return:
        """
        Logger.logger.info("线程监控启动成功")
        while True:
            Monitor.thread_job(*args)
            time.sleep(20)

    @staticmethod
    def thread_job(*args):
        downloader_size = args[0]
        extractor_size = args[1]
        storage_dup_size = args[2]
        dispatch_size = args[3]

        downloader = [re.search(r"(\d+)", name.name).group(1) for name in threading.enumerate() if
                      name.name.__contains__("download")]
        extractor = [re.search(r"(\d+)", name.name).group(1) for name in threading.enumerate() if
                     name.name.__contains__("extractor")]
        storage_dup = [re.search(r"(\d+)", name.name).group(1) for name in threading.enumerate() if
                       name.name.__contains__("storage_dup")]
        dispatch = [re.search(r"(\d+)", name.name).group(1) for name in threading.enumerate() if
                    name.name.__contains__("dispatch")]

        if len(downloader) < downloader_size:
            need_review = [i for i in range(downloader_size) if i not in downloader]
            for index in need_review:
                Logger.logger.info(f"重启线程：download--{index}")
                threading.Thread(target=Downloader(**Crawler.crawler_setting).run, name=f"download--{index}").start()
        if len(extractor) < extractor_size:
            need_review = [i for i in range(extractor_size) if i not in downloader]
            for index in need_review:
                Logger.logger.info(f"重启线程：extractor--{index}")
                threading.Thread(target=Extractor(**Crawler.crawler_setting).run, name=f"extractor--{index}").start()
        if len(storage_dup) < storage_dup_size:
            need_review = [i for i in range(storage_dup_size) if i not in downloader]
            for index in need_review:
                Logger.logger.info(f"重启线程：storage_dup--{index}")
                threading.Thread(target=BaseStorageDup(**Crawler.crawler_setting).run,
                                 name=f"storage_dup--{index}").start()
        if len(dispatch) < dispatch_size:
            need_review = [i for i in range(dispatch_size) if i not in dispatch]
            for index in need_review:
                Logger.logger.info(f"重启线程：dispatch--{index}")
                threading.Thread(target=Dispatch(**Crawler.crawler_setting).run, name=f"dispatch--{index}").start()

    @staticmethod
    def task_monitor():
        Logger.logger.info("任务监控启动成功")
        while True:
            Monitor.task_job()
            time.sleep(1)

    @staticmethod
    def task_job():
        collections = MongoUtil.monitor.list_collections()
        for collection in iter(collections):
            # MongoUtil.monitor.get_collection(task_id).aggregate([{"$indexStats": {}}])
            collection = MongoUtil.monitor.get_collection(collection.get("name"))
            collection_count = collection.count()
            if collection_count == 0:
                Logger.logger.info("删除--{}--集合".format(collection.name))
                collection.drop()