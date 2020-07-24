import hashlib
import time
import uuid
from threading import Thread

import datetime
from crawler4py.download.request import request
from crawler4py.download.process import process
from crawler4py.log import Logger
from crawler4py.crawler import Crawler
from crawler4py.util.rabbitmqutil import connect, get_data, send_data
from crawler4py.util.redisutil import RedisUtil
from crawler4py.util.running_params import task_q, html_q, data_q
from crawler4py.util.sqlutil import SqlUtil


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
            t1 = Thread(target=self.process, name="download-process-{}".format(uuid.uuid4().hex))
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
        if result.get("recovery_flag"):
            if result.get("recovery_flag") < 3:
                send_data(Downloader.mq_conn, '', repr(result), 'recovery')
                Logger.logger.info("回收--{}--成功".format(result.get("task_url")))
            else:
                if message.get("main_task_flag"):
                    while True:
                        if RedisUtil.get_lock():
                            pre_exec_time = message.get("exec_time")
                            exec_time = message.get("exec_time") + datetime.timedelta(seconds=message.get("task_cell"))
                            SqlUtil.update_task(0, "'{}'".format(message.get("task_id")), "'{}'".format(str(exec_time)),
                                                "'{}'".format(str(pre_exec_time)))
                            RedisUtil.release_lock()
                            RedisUtil.release_monitor(message.get("task_id"))
                            break
                        time.sleep(0.3)
                RedisUtil.del_exist(message.get("task_id"),
                                    hashlib.md5(message.get("task_url").encode("utf-8")).hexdigest())
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
                Logger.logger.info("{}--超出回收次数上限， 不做回收".format(result.get("task_url")))
        else:
            send_data(Downloader.mq_conn, '', repr(result), 'extract')
            Logger.logger.info("发送任务至提取中心")
