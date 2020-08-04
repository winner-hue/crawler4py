import sys
import time
from threading import Thread

from crawler4py.dispatch.dispatch import Dispatch
from crawler4py.dispatch.monitor import Monitor
from crawler4py.download.downloader import Downloader
from crawler4py.extractor.extractor import Extractor
from crawler4py.log import Logger
from crawler4py.storage_dup import BaseStorageDup
from crawler4py.util.running_params import task_q

'''启动器'''


class Starter(object):
    __instance = None

    def __init__(self, url=None, **setting):
        if not Starter.__instance:
            # 目前简单模式属于废弃状态， 不必考虑， 后续不会开发，会移除调
            super(Starter, self).__init__()
            self.url = url
            self.setting = setting
            self.crawler_mode = setting.get("crawler_mode") if setting.get("crawler_mode") else 0
            assert (url or self.crawler_mode), "简单模式下，url和爬虫类型不能同时为false"

            dispatch_thread_size = setting.get("dispatch_thread_size") if setting.get(
                "dispatch_thread_size") is not None else 1
            if isinstance(dispatch_thread_size, list):
                self.dispatch_sub = dispatch_thread_size[1:]
                dispatch_thread_size = dispatch_thread_size[0]
            else:
                self.dispatch_sub = [True, True, True]
            self.dispatch_thread_size = dispatch_thread_size
            self.downloader_thread_size = setting.get("downloader_thread_size") if setting.get(
                "downloader_thread_size") is not None else 1
            self.extractor_thread_size = setting.get("extractor_thread_size") if setting.get(
                "extractor_thread_size") is not None else 1
            self.storage_dup_thread_size = setting.get("storage_dup_thread_size") if setting.get(
                "storage_dup_thread_size") is not None else 1

    @classmethod
    def get_instance(cls, url=None, **setting):
        if not Starter.__instance:
            cls.__instance = Starter(url=url, **setting)
        return cls.__instance

    def start(self):
        """
        启动
        :return:
        """
        Logger.get_instance(**self.setting)  # 日志类 创建
        crawler = Dispatch(**self.setting)
        try:
            sys.path.append(self.setting.get("base_dir"))
        except AttributeError:
            pass
        if not self.crawler_mode:
            task_q.put(self.url)
        self.install(crawler)
        crawler.start()
        if self.crawler_mode:
            time.sleep(5)
            self.monitor()

    def install(self, crawler: Dispatch):
        """
        安装各个组件
        :param crawler:
        :return:
        """
        for i in range(self.dispatch_thread_size):
            crawler.installed(Dispatch(**self.setting), crawler.dispatch)
        for i in range(self.downloader_thread_size):
            crawler.installed(Downloader(**self.setting), crawler.downloader)
        for i in range(self.extractor_thread_size):
            crawler.installed(Extractor(**self.setting), crawler.extractor)
        for i in range(self.storage_dup_thread_size):
            crawler.installed(BaseStorageDup(**self.setting), crawler.storage_dup)

    def monitor(self):
        """
        监控器
        :return:
        """
        Thread(target=Monitor.get_instance().thread_monitor,
               args=(self.downloader_thread_size, self.extractor_thread_size, self.storage_dup_thread_size,
                     self.dispatch_thread_size, self.dispatch_sub), name="thread_monitor").start()

        Thread(target=Monitor.get_instance().sys_monitor, name="sys-monitor").start()
