import time
import uuid
from threading import Thread

from crawler4py.log import Logger
from crawler4py.crawler import Crawler
from crawler4py.storage_dup.storage_dup import process
from crawler4py.util.commonutil import get_plugin_path
from crawler4py.util.rabbitmqutil import connect, get_data, send_data, get_queue
from crawler4py.util.redisutil import RedisUtil
from crawler4py.util.running_params import data_q, task_q, html_q
import datetime

from crawler4py.util.sqlutil import SqlUtil


class BaseStorageDup(Crawler):

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
                mq_queue = get_queue(self.crawler_setting, 'storage_dup')
            except AttributeError:
                user = "crawler4py"
                pwd = "crawler4py"
                host = "127.0.0.1"
                port = 5672
                mq_queue = "storage_dup"

            mq_conn = connect(mq_queue, user, pwd, host, port)
            self.call_back(**{"no_ack": None, "channel": mq_conn, "routing_key": mq_queue})

    @staticmethod
    @get_data
    def call_back(ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        message: dict = eval(body.decode())
        Logger.logger.info(message)
        path = get_plugin_path(BaseStorageDup.crawler_setting, 'storage_dup')
        del message["view_source"]
        if not message.get("next_pages"):
            process(message, path)
        else:
            # 非详细页面， 需要先判断临时任务库是否存在，存在则进行处理
            if RedisUtil.monitor_is_exist(message.get("task_id")) and RedisUtil.monitor_ttl(
                    message.get("task_id")) > 10:
                result = process(message, path)

                if len(message.get("next_pages")):
                    mq_queue = get_queue(BaseStorageDup.crawler_setting, 'dispatch')
                    send_data(ch, '', repr(result), mq_queue)
                    Logger.logger.info("发送数据至dispatch进行构造任务")
                else:
                    Logger.logger.info("所有数据都被排掉， 不添加数据")
            else:
                Logger.logger.info("监控集合已经消失或者超出监控时间， 不再发送任务")
        # 每次处理数据， 需要判断当前临时任务的状态， 确定是否关闭
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
