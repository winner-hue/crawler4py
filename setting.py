import os

from util.sqlutil import MySql

setting = {
    "crawler_mode": 1,  # 爬虫模式， 1表示复杂模式， 0表示简单模式
    "mongo": {
        # 初始化mongo排重库
        "mongo_dup": {
            "user": 1,
            "pwd": 1,
            "host": "127.0.0.1",
            "port": 27017
        },
        # 初始化mongo任务监控库
        "mongo_task_monitor": {
            "user": None,
            "pwd": None,
            "host": "127.0.0.1",
            "port": 27017
        },
    },
    "mq": {
        "host": "127.0.0.1",
        "port": 5672,
        "user": "pycrawler",
        "pwd": "pycrawler"
    },
    "logger_path": "{}{}logging.json".format(os.path.dirname(__file__), os.sep),
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
}
