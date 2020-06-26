setting = {
    "crawler_mode": 1,  # 爬虫模式， 1表示集群， 0表示不启用集群模式
    "mongo": {
        # 初始化mongo排重库
        "mongo_dup": {
            "user": None,
            "pwd": None,
            "ip": "127.0.0.1",
            "port": 27017
        },
        # 初始化mongo任务监控库
        "mongo_task_monitor": {
            "user": None,
            "pwd": None,
            "ip": "127.0.0.1",
            "port": 27017
        },
    }
}
