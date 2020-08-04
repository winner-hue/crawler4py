import copy
import time
import uuid
from threading import Thread

from crawler4py.log import Logger
from crawler4py.crawler import Crawler
from crawler4py.util.commonutil import is_send
from crawler4py.util.mongoutil import MongoUtil
from crawler4py.util.rabbitmqutil import connect, send_data, get_data, get_queue, get_login_info
from crawler4py.util.redisutil import RedisUtil
from crawler4py.util.sqlutil import SqlUtil
import datetime


class Dispatch(Crawler):

    def __init__(self, **setting):
        super(Dispatch, self).__init__(**setting)
        self.dispatch = []
        self.dispatch_sub = [True, True, True]  # 调度中心 任务下发，任务生成，任务回收启动配置
        self.downloader = []
        self.extractor = []
        self.storage_dup = []

        # mq连接参数
        self.mq_params = get_login_info(self.crawler_setting)

    def start(self):
        """
        调度中心启动爬虫其他控制中心
        :return:
        """
        for index, dispatch in enumerate(self.dispatch):
            Thread(target=dispatch.run, name=f"dispatch--{index}").start()

        for index, downloader in enumerate(self.downloader):
            Thread(target=downloader.run, name=f"downloader--{index}").start()

        for index, extractor in enumerate(self.extractor):
            Thread(target=extractor.run, name=f"extractor--{index}").start()

        for index, storage_dup in enumerate(self.storage_dup):
            Thread(target=storage_dup.run, name=f"storage_dup--{index}").start()

    def run(self):
        """
        调度中心启动
        :return:
        """
        try:
            Logger.logger.info("dispatch 开始启动。。。")
            t1 = Thread(target=self.process, name="dispatch-{}".format(uuid.uuid4().hex))
            t1.start()
            Logger.logger.info("dispatch 启动成功。。。")
            t1.join()
        except Exception as e:
            Logger.logger.info("dispatch 启动失败：{}".format(e))

    def process(self):
        """
        调度中心启动任务提取，任务回收，任务生成线程
        :return:
        """
        if self.crawler_setting.get("crawler_mode"):
            try:
                RedisUtil.get_instance(**self.crawler_setting)
                SqlUtil.get_instance(**self.crawler_setting.get("sql"))
                MongoUtil.get_instance(**self.crawler_setting)
            except Exception:
                raise Exception("数据库初始化失败， 请检查配置文件")

            dispatch_config = self.crawler_setting.get("dispatch_thread_size")
            if isinstance(dispatch_config, list):
                self.dispatch_sub = dispatch_config[1:]
                self._start()
            else:
                self._start()

    def _start(self):
        """
        启动任务
        :param params:
        :param user:
        :param pwd:
        :param host:
        :param port:
        :return:
        """
        if self.dispatch_sub[0]:
            sql_task = Thread(target=self.get_task, name="sql-task-{}".format(uuid.uuid4().hex))
            sql_task.start()
        if self.dispatch_sub[1]:
            generate_task = Thread(target=self.generate_task, name="generate-task-{}".format(uuid.uuid4().hex))
            generate_task.start()
        if self.dispatch_sub[2]:
            back_task = Thread(target=self.back_task, name="back-task-{}".format(uuid.uuid4().hex))
            back_task.start()

    def get_task(self):
        """
        从数据库中定时获取需要执行的任务，发送至下载队列
        :return:
        """
        task_cell = self.crawler_setting.get("task_cell") if self.crawler_setting.get("task_cell") else 10
        mq_queue = get_queue(self.crawler_setting, 'download')
        mq_conn = connect(mq_queue, self.mq_params[0], self.mq_params[1], self.mq_params[2], self.mq_params[3])
        while True:
            if RedisUtil.get_lock():
                tasks = SqlUtil.get_task()
                if tasks:
                    for task in tasks:
                        task_id = task.get("task_id")
                        RedisUtil.monitor_task(task_id)
                        task["main_task_flag"] = 1
                        message = repr(task)
                        # 判断是否超出队列限制大小，超出则不下发
                        is_send(self.mq_params, self.crawler_setting, mq_queue)
                        send_data(mq_conn, '', message, mq_queue)
                        SqlUtil.update_task(1, "'{}'".format(task_id), "'{}'".format(task.get("exec_time")),
                                            "'{}'".format(task.get("pre_exec_time")))
                    Logger.logger.info("任务发送完成, 开始进行休眠, 休眠..{}s..".format(task_cell))
                else:
                    Logger.logger.info("没有可提取的任务，开始进行休眠，休眠..{}s..".format(task_cell))
                RedisUtil.release_lock()
            else:
                Logger.logger.info("未抢到锁，休眠..{}s..".format(task_cell))
            time.sleep(task_cell)

    def generate_task(self):
        """
        生成任务
        :return:
        """
        mq_queue = get_queue(self.crawler_setting, "dispatch")
        mq_conn_download = connect(mq_queue, self.mq_params[0], self.mq_params[1], self.mq_params[2], self.mq_params[3])
        self.call_back(**{"no_ack": None, "channel": mq_conn_download, "routing_key": mq_queue})

    def back_task(self):
        """
        回收任务
        :return:
        """
        mq_queue = get_queue(self.crawler_setting, "recovery")
        mq_conn_recovery = connect(mq_queue, self.mq_params[0], self.mq_params[1], self.mq_params[2], self.mq_params[3])
        self.call_back(**{"no_ack": None, "channel": mq_conn_recovery, "routing_key": mq_queue})

    @staticmethod
    @get_data
    def call_back(ch, method, properties, body):
        """
        rabitmq 回调消费者汉书， 如果有next_pages 则为生成任务， 没有则为回收任务
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
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
                mq_queue = get_queue(Dispatch.crawler_setting, 'download')
                mq_params = get_login_info(Dispatch.crawler_setting)
                is_send(mq_params, Dispatch.crawler_setting, mq_queue)
                send_data(ch, '', repr(message), mq_queue)
        else:
            send_data(ch, '', repr(message), 'download')
