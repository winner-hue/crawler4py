import os

from crawler4py.util.sqlutil import MySql

BASE_DIR = os.path.dirname(__file__)
setting = {
    "base_dir": BASE_DIR,
    "crawler_mode": 1,  # 爬虫模式， 1表示复杂模式， 0表示简单模式
    # 设置线程数量
    "dispatch_thread_size": 1,
    "downloader_thread_size": 0,
    "extractor_thread_size": 0,
    "storage_dup_thread_size": 0,
    # 限制下载任务队列的大小， 当超出一定值时， 将不再发送任务至下载队列
    "download_task_size_limit": 2,
    # redis 配置
    "redis": {
        # 排重库配置
        "dup": {
            "pwd": None,
            "host": "127.0.0.1",
            "port": 6379,
            "db": 0,
            # 如果使用布隆过滤器， 则需配置
            "bloomfilter": False,
            "blocknum": 1,
        },
        # 临时任务库配置， 用于监控运行中的任务
        "task_monitor": {
            "pwd": None,
            "host": "127.0.0.1",
            "port": 6379,
            "db": 0,
            "expire": 10 * 60
        },
    },
    # mongodb配置
    "mongo": {
        "database": {
            "user": None,
            "pwd": None,
            "host": "127.0.0.1",
            "port": 27017,
            "collection_name": "database"
        }
    },
    # rabbitmq 配置
    "mq": {
        "host": "127.0.0.1",
        "port": 5672,
        "user": "crawler4py",
        "pwd": "crawler4py",
        "api_port": 15672
    },
    # mysql 配置
    "sql": {
        "driver": MySql,
        "user": "crawler4py",
        "pwd": "crawler4py",
        "host": "127.0.0.1",
        "port": 3306,
        "db": "crawler4py"
    },
    # rabbitmq 队列名称配置
    "mq_queue": {
        "download": "",
        "extract": "",
        "storage_dup": "",
        "recovery": "",
        "dispatch": ""
    },
    # 每次获取任务的间隔时间，以秒为单位
    "task_cell": 10,
    # 各个中心插件位置配置
    "plugins": {
        "download": "plugins.download",
        "extract": "plugins.extract",
        "storage_dup": "plugins.storage_dup",
        "dispatch": "plugins.dispatch"
    }
}
