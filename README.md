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

+ 配置
    + 配置mysql
    
        + 用户创建与授权
              
              create user 'crawler4py'@'%' identified by 'crawler4py';
              grant all on *.* to 'crawler4py'@'%';
              
        + 创建数据库
        
              1. create database crawler4py;
              2. crawler4py --create_db (注：根据实际情况配置具体参数，参数擦看---manager --help)
              
        + 创建任务表
              
              1. 运行table.sql中的内容                
              2. crawler4py --create_table
                
        + 添加任务
                
              1. 手动操作数据库添加任务
              2. crawler4py --add_task --task_url 网址

    + 配置setting文件
                      
          setting 配置必须为字典格式
            BASE_DIR = os.path.dirname(__file__)
            setting = {
                "base_dir": BASE_DIR,
                "crawler_mode": 1,  # 爬虫模式， 1表示复杂模式， 0表示简单模式（已废弃）
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
                    "dispatch": "plugins.dispatch"   # 目前没有调度插件，后续增加
                }
            }

+ 使用
    
    + 简单demo 
          
          新建py文件
          输入：
            start = Starter.get_instance(**setting)
            start.start()
          运行即可开启爬虫
    
    + 撰写插件
          
          为不同的站点开发相应的插件， 需要配置setting的plugins。在配置好文件目录、以及任务类型（可选）。具体可以参照项目中plugins文件夹的配置方式
          下载器插件：
               按照网址域名编写py文件， 例如域名为baidu.com, 则py文件应为baidu_com.py
               接着只需要在文件中定义process(task_url, message) 方法， 便可以更改下载逻辑
          提取插件：
               按照网址域名编写py文件， 例如域名为baidu.com, 则py文件应为baidu_com.py
               接着在文件中定义自己的类，类名没有限制，但是需要继承基类 BaseExtract， 按照自己的需要，实现不同的逻辑
          排重入库插件：
               按照网址域名编写py文件， 例如域名为baidu.com, 则py文件应为baidu_com.py
               接着只需要在文件中定义process(task_url, message) 方法， 便可以更改下载逻辑
          
          
  
  
        
    
