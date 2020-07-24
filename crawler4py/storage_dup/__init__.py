import time
import uuid
from threading import Thread

from crawler4py.log import Logger
from crawler4py.crawler import Crawler
from crawler4py.storage_dup.storage_dup import process
from crawler4py.util.rabbitmqutil import connect, get_data, send_data
from crawler4py.util.redisutil import RedisUtil
from crawler4py.util.running_params import data_q, task_q, html_q
import datetime

from crawler4py.util.sqlutil import SqlUtil


class BaseStorageDup(Crawler):
    mq_conn = None

    def simple(self):
        while not task_q.empty() or not html_q.empty() or not data_q.empty():
            task_url = task_q.get()
            Logger.logger.info(task_url)
        else:
            Logger.logger.info("监测到退出信号，开始退出。。。")

    def run(self):
        try:
            Logger.logger.info("storage_dup 开始启动。。。")
            t1 = Thread(target=self.process, name="storage-dup-process-{}".format(uuid.uuid4().hex))
            t1.start()
            Logger.logger.info("storage_dup 启动成功。。。")
            t1.join()
        except Exception as e:
            Logger.logger.info("storage_dup 启动失败：{}".format(e))

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
                mq_queue = self.crawler_setting.get("mq_queue").get("storage_dup")
                if not mq_queue:
                    mq_queue = "storage_dup"
            except AttributeError:
                user = "pycrawler"
                pwd = "pycrawler"
                host = "127.0.0.1"
                port = 5672
                mq_queue = "storage_dup"

            BaseStorageDup.mq_conn = connect(mq_queue, user, pwd, host, port)
            self.call_back(**{"no_ack": None, "channel": BaseStorageDup.mq_conn, "routing_key": mq_queue})

    @staticmethod
    @get_data
    def call_back(ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        message: dict = eval(body.decode())
        try:
            path = BaseStorageDup.crawler_setting.get("plugins").get("storage_dup")
        except AttributeError:
            path = None
        del message["view_source"]
        if not message.get("next_pages"):
            process(message, path)
        else:
            if RedisUtil.monitor_is_exist(message.get("task_id")) and RedisUtil.monitor_ttl(
                    message.get("task_id")) > 10:
                result = process(message, path)

                if len(message.get("next_pages")):
                    send_data(BaseStorageDup.mq_conn, '', repr(result), 'dispatch')
                    Logger.logger.info("发送数据至dispatch进行构造任务")
                else:
                    Logger.logger.info("所有数据都被排掉， 不添加数据")
            else:
                Logger.logger.info("监控集合已经消失或者超出监控时间， 不再发送任务")
        if not RedisUtil.monitor_score(message.get("task_id")):
            RedisUtil.release_monitor(message.get("task_id"))
            while True:
                if RedisUtil.get_lock():
                    pre_exec_time = message.get("exec_time")
                    exec_time = datetime.datetime.now() + datetime.timedelta(seconds=message.get("task_cell"))
                    SqlUtil.update_task(0, "'{}'".format(message.get("task_id")), "'{}'".format(str(exec_time)),
                                        "'{}'".format(str(pre_exec_time)))
                    RedisUtil.release_lock()
                    break
                time.sleep(0.3)
