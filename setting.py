import os

from util.sqlutil import MySql

setting = {
    "crawler_mode": 0,  # 爬虫模式， 1表示集群， 0表示不启用集群模式
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
        "type": 1,  # 0表示kafka，1表示rabbitmq
        "host": "127.0.0.1",
        "port": 5672,
        "user": "pycrawler",
        "pwd": "pycrawler"
    },
    "logger_path": "{}{}logging.json".format(os.path.dirname(__file__), os.sep),
    "sql": {
        "driver": MySql,
        "user": "root",
        "pwd": "root",
        "host": "127.0.0.1",
        "port": 3306,
        "db": "pycrawler"
    }
}
