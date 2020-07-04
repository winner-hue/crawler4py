from threading import Thread

from download import request
from download.callback import call_back
from log import Logger
from pycrawler import Crawler
from util.rabbitmqutil import connect
from util.running_params import task_q, html_q, data_q


class Downloader(Crawler):

    def simple(self):
        while not task_q.empty() or not html_q.empty() or not data_q.empty():
            task_url = task_q.get()
            Logger.logger.info(task_url)
            r = request.request().get(task_url)
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

            mq_conn = connect(mq_queue, user, pwd, host, port)
            call_back(**{"no_ack": None, "channel": mq_conn, "routing_key": mq_queue})
