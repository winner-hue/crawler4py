import hashlib
import time
import uuid
from threading import Thread

import datetime
from crawler4py.download.request import request
from crawler4py.download.process import process
from crawler4py.log import Logger
from crawler4py.crawler import Crawler
from crawler4py.util.commonutil import get_plugin_path
from crawler4py.util.rabbitmqutil import connect, get_data, send_data, get_queue
from crawler4py.util.redisutil import RedisUtil
from crawler4py.util.running_params import task_q, html_q, data_q
from crawler4py.util.sqlutil import SqlUtil


class Downloader(Crawler):

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
                mq_queue = get_queue(self.crawler_setting, "download")
            except AttributeError:
                user = "crawler4py"
                pwd = "crawler4py"
                host = "127.0.0.1"
                port = 5672
                mq_queue = "download"
            mq_conn = connect(mq_queue, user, pwd, host, port)
            try:
                plugin_path = self.crawler_setting.get("plugins").get("download")
            except ArithmeticError:
                plugin_path = None
            self.call_back(
                **{"no_ack": None, "channel": mq_conn, "routing_key": mq_queue, "plugin_path": plugin_path})

    @staticmethod
    @get_data
    def call_back(ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        message: dict = eval(body.decode())
        path = get_plugin_path(Downloader.crawler_setting, 'download')
        result = process(message, path)
        if result.get("recovery_flag"):
            if result.get("recovery_flag") < 3:
                mq_queue = get_queue(Downloader.crawler_setting, "recovery")
                send_data(ch, '', repr(result), mq_queue)
                Logger.logger.info("回收--{}--成功".format(result.get("task_url")))
            else:
                # 主任务回收， 则需要更新任务状态， 以及清除调在redis中生成的临时任务库
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
                # 任务下载失败， 都需要清除调redis临时任务库中的url
                RedisUtil.del_exist(message.get("task_id"),
                                    hashlib.md5(message.get("task_url").encode("utf-8")).hexdigest())

                # 进行判断， 如果redis临时任务库中所有的数据的分没有10， 则关闭任务（注：分值为10表示详细页面， 分值为100表示列表页面）
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
            mq_queue = get_queue(Downloader.crawler_setting, "extract")
            send_data(ch, '', repr(result), mq_queue)
            Logger.logger.info(result)
            Logger.logger.info("发送任务至提取中心")
