import sys
from threading import Thread

from extractor.callback import call_back
from log import Logger
from pycrawler import Crawler
from util.rabbitmqutil import connect
from util.running_params import html_q


class Extractor(Crawler):
    def simple(self):
        while True:
            task_url = html_q.get()
            print(task_url)
            single_over_signal = 1
            exit()

    def run(self):
        try:
            Logger.logger.info("extract 开始启动。。。")
            t1 = Thread(target=self.process)
            t1.start()
            Logger.logger.info("extract 启动成功。。。")
            t1.join()
        except Exception as e:
            Logger.logger.info("extract 启动失败：{}".format(e))

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
                mq_queue = self.crawler_setting.get("mq_queue").get("extract")
                if not mq_queue:
                    mq_queue = "extract"
            except AttributeError:
                user = "pycrawler"
                pwd = "pycrawler"
                host = "127.0.0.1"
                port = 5672
                mq_queue = "extract"

            mq_conn = connect(mq_queue, user, pwd, host, port)
            call_back(**{"no_ack": None, "channel": mq_conn, "routing_key": mq_queue})
