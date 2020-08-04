import re
import sys
import threading
import time

import psutil

from crawler4py.dispatch.dispatch import Dispatch
from crawler4py.download.downloader import Downloader
from crawler4py.extractor.extractor import Extractor
from crawler4py.log import Logger
from crawler4py.crawler import Crawler
from crawler4py.storage_dup import BaseStorageDup

'''监控器'''


class Monitor(object):
    __instance = None
    lock = threading.Lock()

    def __init__(self):
        if Monitor.__instance:
            Logger.logger.info("monitor已经初始化")
        else:
            Logger.logger.info("monitor开始初始化")

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.lock.acquire()
            cls.__instance = Monitor()
            Logger.logger.info("monitor初始化成功")
            cls.lock.release()
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
        """
        线程监控
        :param args: 0:下载线程数量,1:解析线程数量,2:入库排重线程数量,3:调度线程数量,4:调度中心启动任务判断
        :return: 
        """
        downloader_size = args[0]
        extractor_size = args[1]
        storage_dup_size = args[2]
        dispatch_size = args[3]
        dispatch_sub = args[4]

        # 获取正在运行的线程数量
        downloader = [re.search(r"(\d+)", name.name).group(1) for name in threading.enumerate() if
                      name.name.__contains__("download")]
        extractor = [re.search(r"(\d+)", name.name).group(1) for name in threading.enumerate() if
                     name.name.__contains__("extractor")]
        storage_dup = [re.search(r"(\d+)", name.name).group(1) for name in threading.enumerate() if
                       name.name.__contains__("storage_dup")]

        sql_task = [re.search(r"(\w+)", name.name).group(1) for name in threading.enumerate() if
                    name.name.__contains__("sql-task-")]
        generate_task = [re.search(r"(\w+)", name.name).group(1) for name in threading.enumerate() if
                         name.name.__contains__("generate-task-")]
        back_task = [re.search(r"(\w+)", name.name).group(1) for name in threading.enumerate() if
                     name.name.__contains__("back-task-")]

        # 如果线程的数量小于初始化数量， 则重启线程
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
        if dispatch_sub[1]:
            if len(generate_task) < dispatch_size:
                need_review = [i for i in range(dispatch_size) if i not in generate_task]
                for index in need_review:
                    Logger.logger.info(f"重启线程：generate-task-{index}")
                    threading.Thread(target=Dispatch(**Crawler.crawler_setting).generate_task,
                                     name=f"generate-task-{index}").start()
        if dispatch_sub[2]:
            if len(back_task) < dispatch_size:
                need_review = [i for i in range(dispatch_size) if i not in back_task]
                for index in need_review:
                    Logger.logger.info(f"重启线程：back-task-{index}")
                    threading.Thread(target=Dispatch(**Crawler.crawler_setting).back_task,
                                     name=f"back-task-{index}").start()
        if dispatch_sub[0]:
            if len(sql_task) < dispatch_size:
                need_review = [i for i in range(dispatch_size) if i not in sql_task]
                for index in need_review:
                    Logger.logger.info(f"重启线程：back-task-{index}")
                    threading.Thread(target=Dispatch(**Crawler.crawler_setting).get_task,
                                     name=f"back-task-{index}").start()

    @staticmethod
    def sys_monitor():
        """
        系统监控， 监听系统cpu，内存等状态，
        当超过阈值则通知运维人员, 此处改为停掉系统
        :return:
        """
        while True:
            cpu_per = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent

            if memory > 99:
                Logger.logger.info("系统退出：cpu状态：{}, 内存状态：{}".format(cpu_per, memory))
                sys.exit(0)
            else:
                Logger.logger.info("cpu状态：{}, 内存状态：{}".format(cpu_per, memory))
            time.sleep(20)
