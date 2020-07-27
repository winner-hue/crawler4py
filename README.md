# crawler4py
> ##  A distributed crawler framework based on Python

> **install**

+ 安装
        
    +   1.安装crawler4py
            
            pip install crawler4py
        
    +   2.安装redis
            
            说明：redis用来进行排重，支持集合排重和布隆过滤器排重
                
            centos：
                1： yum install redis-server -y
                2： [redis官网](https://redis.io/download)
            ubuntu: 
                
                1： sudo apt-get install redis-server
                2： [redis官网](https://redis.io/download)
  
    +   3.安装mysql
            
            说明：mysql用来作为任务库，关系型数据库方便对任务进行监控和修改
                
            centos: 
                1： yum install mysql-server -y
                2： [mysql官网](https://dev.mysql.com/doc/refman/8.0/en/linux-installation.html)
            ubuntu: 
                1： sudo apt-get install mysql-server
                2： [mysql官网](https://dev.mysql.com/doc/refman/8.0/en/linux-installation.html)
  
    +   4.安装MongoDB
            
            说明：MongoDB用来存储数据
                
            centos: 
                1： yum install mongod-server -y
                2： [mongodb官网](https://docs.mongodb.com/manual/installation/)
            ubuntu: 
                1： sudo apt-get install mongod-server
                2： [mongodb官网](https://docs.mongodb.com/manual/installation/)
  
    +   5.安装rabbitmq
            
            说明：rabbitmq用来作为消息中转站
                
            centos 
                yum install erlang-nox
                yum install rabbitmq-server
                    
                可选（此处是通过命令，也可以通过界面的方式来添加）：
                    rabbitmqctl add_user crawler4py crawler4py  
                    rabbitmqctl set_user_tags crawler4py administrator
                    rabbitmqctl set_permissions -p crawler4py crawler4py '.*' '.*' '.*'
            ubuntu: 
                sudo apt-get install erlang-nox
                ssudo apt-get install rabbitmq-server
                
                可选（此处是通过命令，也可以通过界面的方式来添加）：
                    sudo rabbitmqctl add_user crawler4py crawler4py  
                    sudo rabbitmqctl set_user_tags crawler4py administrator
                    sudo rabbitmqctl set_permissions -p crawler4py crawler4py '.*' '.*' '.*'
> **Tutorial & Usage**

+ 配置
    + 配置mysql
        + 创建数据库
        + 用户创建与授权
        + 创建任务表
        + 添加任务

    + 配置setting文件
                      
          setting 配置必须为字典格式
           setting = {
               "base_dir": BASE_DIR, # 当前目录路径 一般为os.path.dirname(__file__)
               "crawler_mode": 1,  # 爬虫模式， 1表示集群模式， 0 表示简单单机模式（目前尚不支持）
               # 设置线程数量
               "dispatch_thread_size": 1, # 调度中心线程数量
               "downloader_thread_size": 1, # 下载器线程数量
               "extractor_thread_size": 1, # 提取器线程数量
               "storage_dup_thread_size": 1, # 入库排重线程数量
               # 排重库和任务监控库配置
               "redis": {
                   # 排重库配置
                   "dup": {
                       "pwd": None,
                       "host": "127.0.0.1", 
                       "port": 6379,
                       "db": 0,
                       "bloomfilter": False, # 是否采用布隆过滤器，未配置情况默认false
                       "blocknum": 1, # 布隆过滤器块设置， 1个块表示256M
                       "key": "bloomfilter" # key表示在排重库在redis中的名称
                   },
                   # 任务监控库配置
                   "task_monitor": {
                       "pwd": None,
                       "host": "127.0.0.1",
                       "port": 6379,
                       "db": 0,
                       "expire": 10 * 60 # 表示任务过期时间， 如果任务在规定时间未跑完，则关闭任务，默认10分钟
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
               # rabbitmq 配置
               "mq": {
                   "host": "127.0.0.1", 
                   "port": 5672,
                   "user": "crawler4py",
                   "pwd": "crawler4py"
               },
               # 日志配置
               "logger_path": "{}{}logging.json".format(BASE_DIR, os.sep),
               
               # mysql 任务数据库配置
               "sql": {
                   "driver": MySql,
                   "user": "crawler4py",
                   "pwd": "crawler4py",
                   "host": "127.0.0.1",
                   "port": 3306,
                   "db": "crawler4py"
               },
               
               # 队列名称配置
               "mq_queue": {
                   "download": "", # 下载队列名称
                   "extract": "", # 提取队列名称
                   "storage_dup": "", # 入库排重队列名称
                   "recovery": "", # 回收队列名称
                   "dispatch": "" # 调度队列名称
               },
               
               # 获取任务时间间隔
               "task_cell": 10,
               
               # 插件位置
               "plugins": {
                   "download": "plugins.download", # 下载插件位置
                   "extract": "plugins.extract", # 提取插件位置
                   "storage_dup": "plugins.storage_dup", # 排重入库插件位置
                   "dispatch": "plugins.dispatch" # 调度插件位置
               }
           }
+ 使用
    
    + 编写crawler 
          
          新建一个py文件
          输入：
            start = Starter.get_instance(**setting)
            start.start()
          即可开启爬虫
          
          
  
  
        
    
