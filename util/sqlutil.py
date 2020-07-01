import pymysql
from DBUtils.PooledDB import PooledDB

from log import Logger


class SqlUtil(object):
    __instance = None
    conn = None
    cursor = None

    def __init__(self):
        if self.__instance:
            Logger.logger.info("SqlUtil已经进行初始化")
        else:
            Logger.logger.info("开始进行SqlUtil初始化")

    @classmethod
    def get_instance(cls, **kwargs):
        if not cls.__instance:
            cls.__instance = SqlUtil()
            cls.conn = kwargs.get("driver").get_instance(**kwargs).conn
            cls.cursor = kwargs.get("driver").get_instance(**kwargs).cursor
            Logger.logger.info("SqlUtil初始化成功")
        return cls.__instance

    @classmethod
    def get_task(cls):
        sql = "select * from tasks where task_status=0 order by exec_time asc limit 50"
        cls.cursor.execute(sql)
        return cls.cursor.fetchall()

    @classmethod
    def update_task(cls, task_ids):
        sql = "update tasks set task_status=1 where task_id in ({})".format(','.join(task_ids))
        cls.cursor.execute(sql)
        cls.conn.commit()

    @classmethod
    def insert(cls, sql):
        cls.cursor.execute(sql)
        cls.conn.commit()

    def update(self):
        raise NotImplemented

    def delete(self):
        raise NotImplemented

    def select(self):
        raise NotImplemented


class MySql(object):
    __instance = None

    def __init__(self):
        if not MySql.__instance:
            Logger.logger.info("开始创建mysql实例")
        else:
            Logger.logger.info("已经存在mysql实例")

    @classmethod
    def get_instance(cls, **kwargs):
        if not cls.__instance:
            cls.__instance = MySql()
            user = kwargs.get("user")
            pwd = kwargs.get("pwd")
            host = kwargs.get("host")
            port = kwargs.get("port")
            db = kwargs.get("db")
            cls.pool = PooledDB(pymysql, mincached=1, maxcached=1, maxconnections=3, host=host, user=user, password=pwd,
                                database=db, port=port, cursorclass=pymysql.cursors.DictCursor,
                                setsession=['SET AUTOCOMMIT = 1'])

            cls.conn = cls.pool.connection()

            cls.cursor = cls.conn.cursor(pymysql.cursors.DictCursor)
            Logger.logger.info("mysql实例创建成功")
        return cls.__instance
