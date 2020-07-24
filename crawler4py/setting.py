import os

from crawler4py.util.sqlutil import MySql

BASE_DIR = os.path.dirname(__file__)
setting = {
    "base_dir": BASE_DIR,
    "crawler_mode": 1,  # 爬虫模式， 1表示复杂模式， 0表示简单模式
    # 设置线程数量
    "dispatch_thread_size": 1,
    "downloader_thread_size": 1,
    "extractor_thread_size": 1,
    "storage_dup_thread_size": 1,
    "redis": {
        "dup": {
            "pwd": None,
            "host": "127.0.0.1",
            "port": 6379,
            "db": 0,
            "bloomfilter": False,
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
    "mongo": {
        # 入库
        "database": {
            "user": None,
            "pwd": None,
            "host": "127.0.0.1",
            "port": 27017,
            "collection_name": "database"
        }
    },
    "mq": {
        "host": "127.0.0.1",
        "port": 5672,
        "user": "crawler4py",
        "pwd": "crawler4py"
    },
    "sql": {
        "driver": MySql,
        "user": "crawler4py",
        "pwd": "crawler4py",
        "host": "127.0.0.1",
        "port": 3306,
        "db": "crawler4py"
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
        "storage_dup": "plugins.storage_dup",
        "dispatch": "plugins.dispatch"
    }
}
