# PyCrawler
> #####A distributed crawler framework based on Python

> **install**

+ 安装依赖包
        
    +   1.安装依赖包
               
            pip install -r requests.txt
        
    +   2.安装redis
            
            centos：yum install redis -y
            ubuntu: sudo apt-get install redis -y
  
    +   3.安装mysql
    
            centos: yum install mysql -y
            ubuntu: sudo apt-get install mysql -y
  
    +   4.安装mongodb
    
            centos: yum install mongod -y
            ubuntu: sudo apt-get install mongod -y
  
    +   5.安装rabbitmq
            
            centos yum install rabbitmq -y
            ubuntu: sudo apt-get install rabbitmq -y
            
> **Tutorial & Usage**

+ 使用
    + 配置setting文件
    
    + 添加mysql任务表
    
    + 编写crawler 
          
          新建test.py文件
          输入：
            start = Starter.get_instance(**setting)
            start.start()
          即可开启爬虫
          
          
  
  
        
    
