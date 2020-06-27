import pymysql
from DBUtils.PooledDB import PooledDB

from log import Logger


class SqlUtil(object):
    __instance = None
    conn = None
    cursor = None

    def __init__(self):
        if self.__instance:
            Logger.logger.info("已经进行初始化")
        else:
            Logger.logger.info("开始进行初始化")

    @classmethod
    def get_instance(cls, **kwargs):
        if not cls.__instance:
            cls.__instance = kwargs.get("driver")(**kwargs)
        return cls.__instance

    def insert(self):
        raise NotImplemented

    def update(self):
        raise NotImplemented

    def delete(self):
        raise NotImplemented

    def select(self):
        raise NotImplemented


class MySql(SqlUtil):
    def __init__(self, **kwargs):
        super(MySql, self).__init__()
        user = kwargs.get("user")
        pwd = kwargs.get("pwd")
        host = kwargs.get("host")
        port = kwargs.get("port")
        db = kwargs.get("db")
        pool = PooledDB(pymysql, mincached=1, maxcached=1, maxconnections=3, host=host, user=user, password=pwd,
                        database=db, port=port, cursorclass=pymysql.cursors.DictCursor,
                        setsession=['SET AUTOCOMMIT = 1'])
        MySql.conn = pool.connection()
        MySql.cursor = MySql.conn.cursor(pymysql.cursors.DictCursor)

    def insert(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def select(self):
        pass
