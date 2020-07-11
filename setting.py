import os

from util.sqlutil import MySql

BASE_DIR = os.path.dirname(__file__)
setting = {
    "base_dir": BASE_DIR,
    "crawler_mode": 1,  # 爬虫模式， 1表示复杂模式， 0表示简单模式
    "redis": {
        "dup": {
            "pwd": None,
            "host": "127.0.0.1",
            "port": 6379,
            "db": 0,
            "bloomfilter": True,
            "blocknum": 1,
            "key": "bloomfilter"
        },
        "task_monitor": {
            "pwd": None,
            "host": "127.0.0.1",
            "port": 6379,
            "db": 0,
            "expire": 10 * 60
        },
    },
    # "mongo": {
    #     # 初始化mongo排重库
    #     "mongo_dup": {
    #         "user": None,
    #         "pwd": None,
    #         "host": "127.0.0.1",
    #         "port": 27017
    #     },
    #     # 初始化mongo任务监控库
    #     "mongo_task_monitor": {
    #         "user": None,
    #         "pwd": None,
    #         "host": "127.0.0.1",
    #         "port": 27017
    #     },
    # },
    "mq": {
        "host": "127.0.0.1",
        "port": 5672,
        "user": "pycrawler",
        "pwd": "pycrawler"
    },
    "logger_path": "{}{}logging.json".format(BASE_DIR, os.sep),
    "sql": {
        "driver": MySql,
        "user": "pycrawler",
        "pwd": "pycrawler",
        "host": "127.0.0.1",
        "port": 3306,
        "db": "pycrawler"
    },
    "mq_queue": {
        "download": "",
        "extract": "",
        "storage_dup": "",
        "recovery": "",
        "dispatch": ""
    },
    "task_cell": 10,
    "plugins": {
        "download": "plugins.download",
        "extract": "plugins.extract",
        "storage": "plugins.storage",
        "dup": "plugins.dup",
        "dispatch": "plugins.dispatch"
    }
}
