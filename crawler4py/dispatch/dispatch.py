import copy
import time
import uuid
from threading import Thread

from crawler4py.log import Logger
from crawler4py.crawler import Crawler
from crawler4py.util.mongoutil import MongoUtil
from crawler4py.util.rabbitmqutil import connect, send_data, get_data
from crawler4py.util.redisutil import RedisUtil
from crawler4py.util.sqlutil import SqlUtil
import datetime


class Dispatch(Crawler):
    mq_conn_download = None
    mq_conn_recovery = None

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
            Thread(target=storage_dup.run, name=f"storage_dup--{index}").start()

    def run(self):
        try:
            Logger.logger.info("dispatch 开始启动。。。")
            t1 = Thread(target=self.process)
            t1.start()
            Logger.logger.info("dispatch 启动成功。。。")
            t1.join()
        except Exception as e:
            Logger.logger.info("dispatch 启动失败：{}".format(e))

    def process(self):
        if self.crawler_setting.get("crawler_mode"):
            try:
                RedisUtil.get_instance(**self.crawler_setting)
                SqlUtil.get_instance(**self.crawler_setting.get("sql"))
                MongoUtil.get_instance(**self.crawler_setting)
            except Exception:
                raise Exception("数据库初始化失败， 请检查配置文件")
            try:
                user = self.crawler_setting.get("mq").get("user")
                pwd = self.crawler_setting.get("mq").get("pwd")
                host = self.crawler_setting.get("mq").get("host")
                port = self.crawler_setting.get("mq").get("port")
            except AttributeError:
                user = "crawler4py"
                pwd = "crawler4py"
                host = "127.0.0.1"
                port = 5672
            sql_task = Thread(target=self.get_task, name="sql-task-{}".format(uuid.uuid4().hex),
                              args=(user, pwd, host, port))
            generate_task = Thread(target=self.generate_task, name="generate-task-{}".format(uuid.uuid4().hex),
                                   args=(user, pwd, host, port))
            back_task = Thread(target=self.back_task, name="back-task-{}".format(uuid.uuid4().hex),
                               args=(user, pwd, host, port))
            sql_task.start()
            generate_task.start()
            back_task.start()
            sql_task.join()
            generate_task.join()
            back_task.join()

    def get_task(self, user, pwd, host, port):
        """
        从数据库中定时获取需要执行的任务，发送至下载队列
        :return:
        """
        task_cell = self.crawler_setting.get("task_cell") if self.crawler_setting.get("task_cell") else 10
        try:
            mq_queue = self.crawler_setting.get("mq_queue").get("download")
            if not mq_queue:
                mq_queue = "download"
        except AttributeError:
            mq_queue = "download"
        mq_conn = connect(mq_queue, user, pwd, host, port)
        while True:
            tasks = None
            if RedisUtil.get_lock():
                tasks = SqlUtil.get_task()
                task_ids = ["'{}'".format(task.get("task_id")) for task in tasks]
                if task_ids:
                    SqlUtil.update_task(1, task_ids)
                for task in tasks:
                    task_id = task.get("task_id")
                    RedisUtil.monitor_task(task_id)
                    task["main_task_flag"] = 1
                    message = repr(task)
                    send_data(mq_conn, '', message, mq_queue)
                    Logger.logger.info("任务发送完成, 开始进行休眠, 休眠..{}s..".format(task_cell))
                RedisUtil.release_lock()
            if not tasks:
                Logger.logger.info("未抢到锁或没有可提取任务，休眠..{}s..".format(task_cell))
            time.sleep(task_cell)

    def generate_task(self, user, pwd, host, port):
        try:
            mq_queue = self.crawler_setting.get("mq_queue").get("dispatch")
            if not mq_queue:
                mq_queue = "dispatch"
        except AttributeError:
            mq_queue = "dispatch"
        Dispatch.mq_conn_download = connect(mq_queue, user, pwd, host, port)

        self.call_back(**{"no_ack": None, "channel": Dispatch.mq_conn_download, "routing_key": mq_queue})

    def back_task(self, user, pwd, host, port):
        try:
            mq_queue = self.crawler_setting.get("mq_queue").get("recovery")
            if not mq_queue:
                mq_queue = "recovery"
        except AttributeError:
            mq_queue = "recovery"
        Dispatch.mq_conn_recovery = connect(mq_queue, user, pwd, host, port)

        self.call_back(**{"no_ack": None, "channel": Dispatch.mq_conn_recovery, "routing_key": mq_queue})

    @staticmethod
    @get_data
    def call_back(ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        message: dict = eval(body.decode())
        if message.get("next_pages"):
            next_pages = copy.deepcopy(message.get("next_pages"))
            del message["next_pages"]
            for result in next_pages:
                url = result.get("url")
                header = result.get("header")
                message["task_url"] = url
                message["main_task_flag"] = 0
                message["is_detail"] = result.get("is_detail")
                if header:
                    message["header"] = header
                Logger.logger.info("新任务：{}".format(message))
                send_data(Dispatch.mq_conn_download, '', repr(message), 'download')
        else:
            send_data(Dispatch.mq_conn_recovery, '', repr(message), 'download')
