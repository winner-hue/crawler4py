import uuid
from threading import Thread

from crawler4py.extractor.analysis import process
from crawler4py.log import Logger
from crawler4py.crawler import Crawler
from crawler4py.util.rabbitmqutil import connect, get_data, send_data
from crawler4py.util.running_params import html_q, task_q, data_q
import datetime


class Extractor(Crawler):
    mq_conn = None

    def simple(self):
        while not task_q.empty() or not html_q.empty() or not data_q.empty():
            task_url = task_q.get()
            Logger.logger.info(task_url)
        else:
            Logger.logger.info("监测到退出信号，开始退出。。。")

    def run(self):
        try:
            Logger.logger.info("extract 开始启动。。。")
            t1 = Thread(target=self.process, name="extract-process-{}".format(uuid.uuid4().hex))
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
                user = "crawler4py"
                pwd = "crawler4py"
                host = "127.0.0.1"
                port = 5672
                mq_queue = "extract"

            Extractor.mq_conn = connect(mq_queue, user, pwd, host, port)
            self.call_back(**{"no_ack": None, "channel": Extractor.mq_conn, "routing_key": mq_queue})

    @staticmethod
    @get_data
    def call_back(ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        message: dict = eval(body.decode())
        try:
            path = Extractor.crawler_setting.get("plugins").get("extract")
        except AttributeError:
            path = None
        result = process(message, path)
        send_data(Extractor.mq_conn, '', repr(result), 'storage_dup')
        Logger.logger.info("发送任务至排重入库")
