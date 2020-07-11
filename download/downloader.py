from threading import Thread

import datetime
from download.request import request
from download.process import process
from log import Logger
from pycrawler import Crawler
from util.rabbitmqutil import connect, get_data, send_data
from util.running_params import task_q, html_q, data_q


class Downloader(Crawler):
    mq_conn = None

    def simple(self):
        while not task_q.empty() or not html_q.empty() or not data_q.empty():
            task_url = task_q.get()
            Logger.logger.info(task_url)
            r = request.get(task_url)
            Logger.logger.info(r.request.headers)
            Logger.logger.info("status code: {}".format(r.status_code))
        else:
            Logger.logger.info("监测到退出信号，开始退出。。。")

    def run(self):
        try:
            Logger.logger.info("downloader 开始启动。。。")
            t1 = Thread(target=self.process)
            t1.start()
            Logger.logger.info("downloader 启动成功。。。")
            t1.join()
        except Exception as e:
            Logger.logger.info("downloader 启动失败：{}".format(e))

    def process(self):
        crawler_mode = self.crawler_setting.get("crawler_mode")
        if not crawler_mode:
            self.simple()
        else:
            try:
                user = self.crawler_setting.get("mq").get("user")
                pwd = self.crawler_setting.get("mq").get("pwd")
                host = self.crawler_setting.get("mq").get("host")
                port = self.crawler_setting.get("mq").get("port")
                mq_queue = self.crawler_setting.get("mq_queue").get("download")
                if not mq_queue:
                    mq_queue = "download"
            except AttributeError:
                user = "pycrawler"
                pwd = "pycrawler"
                host = "127.0.0.1"
                port = 5672
                mq_queue = "download"
            Downloader.mq_conn = connect(mq_queue, user, pwd, host, port)
            try:
                plugin_path = self.crawler_setting.get("plugins").get("download")
            except ArithmeticError:
                plugin_path = None
            self.call_back(
                **{"no_ack": None, "channel": Downloader.mq_conn, "routing_key": mq_queue, "plugin_path": plugin_path})

    @staticmethod
    @get_data
    def call_back(ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        message: dict = eval(body.decode())
        try:
            path = Downloader.crawler_setting.get("plugins").get("download")
        except AttributeError:
            path = None
        result = process(message, path)
        if result.get("recovery"):
            send_data(Downloader.mq_conn, '', repr(result), 'recovery')
            Logger.logger.info("回收任务成功")
        else:
            send_data(Downloader.mq_conn, '', repr(result), 'extract')
            Logger.logger.info("发送任务至提取中心")
