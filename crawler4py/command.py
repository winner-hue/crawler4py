import hashlib
from datetime import datetime

import pymysql
from redis import Redis


def connect_sql(**kwargs):
    host = kwargs.get("host") if kwargs.get("host") else "127.0.0.1"
    user = kwargs.get("user") if kwargs.get("user") else "crawler4py"
    password = kwargs.get("password") if kwargs.get("password") else "crawler4py"
    port = kwargs.get("port") if kwargs.get("port") else 3306
    if not kwargs.get("db"):
        database = kwargs.get("db_name") if kwargs.get("db_name") else "crawler4py"
        conn = pymysql.connect(host=host, user=user, password=password, database=database, port=port)
        cursor = conn.cursor()
        return conn, cursor
    else:
        conn = pymysql.connect(host=host, user=user, password=password, port=port)
        cursor = conn.cursor()
        return conn, cursor


def create_db(**kwargs):
    kwargs["db"] = True
    conn, cursor = connect_sql(**kwargs)
    db_name = kwargs.get("db_name") if kwargs.get("db_name") else "crawler4py"
    cursor.execute("show databases")
    for db in cursor:
        if db_name in db:
            print("该数据库已经存在")
            return
    cursor.execute("create database {}".format(db_name))
    print("数据库创建成功")


def create_table(**kwargs):
    conn, cursor = connect_sql(**kwargs)
    sql = "create table tasks\
        (\
          task_id       char(32)                               not null comment '任务id为任务url的md5值' \
            primary key, \
          task_url      varchar(500)                           null comment '任务url',\
          task_cell     int unsigned default '3600'            null comment '任务时间间隔',\
          exec_time     datetime     default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,\
          pre_exec_time datetime     default CURRENT_TIMESTAMP null,\
          task_type     int unsigned                           null comment '任务类型',\
          task_status   int unsigned default '0'               null comment '任务状态',\
          task_add_time datetime     default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '任务添加时间',\
          task_encode   varchar(10)                            null\
        )"
    cursor.execute(sql)
    conn.commit()
    print(True)


def drop_db(**kwargs):
    kwargs["db"] = True
    conn, cursor = connect_sql(**kwargs)
    db_name = kwargs.get("db_name") if kwargs.get("db_name") else "crawler4py"
    cursor.execute("show databases")
    flag = False
    for db in cursor:
        if db_name in db:
            cursor.execute("drop database {}".format(db_name))
            flag = True
            break
    if flag:
        print("数据库删除成功")
    else:
        print("数据库删除失败")


def add_task(**kwargs):
    conn, cursor = connect_sql(**kwargs)

    task_url = kwargs.get("task_url")
    task_cell = kwargs.get("task_cell") if kwargs.get("task_cell") else 3600
    exec_time = kwargs.get("exec_time") if kwargs.get("exec_time") else datetime.now()
    task_type = kwargs.get("task_type") if kwargs.get("task_type") else 'null'
    task_encode = kwargs.get("task_encode") if kwargs.get("task_encode") else 'null'

    task_id = hashlib.md5(task_url.encode("utf-8")).hexdigest()
    sql = "insert into tasks(task_id, task_url, task_cell, exec_time, task_type,task_encode) values('{}','{}','{}','{}',{},{})".format(
        task_id,
        task_url, task_cell, exec_time, task_type,
        task_encode)
    cursor.execute(sql)
    conn.commit()
    print("添加成功")


def delete_task(**kwargs):
    conn, cursor = connect_sql(**kwargs)
    task_url = kwargs.get("task_url")
    task_id = hashlib.md5(task_url.encode("utf-8")).hexdigest()
    sql = "delete from tasks where task_id='{}'".format(task_id)
    result = cursor.execute(sql)
    conn.commit()
    if result:
        print("删除成功")
    else:
        print("删除失败")


# no_sql
def connect_redis(**kwargs):
    host = kwargs.get("host") if kwargs.get("host") else "127.0.0.1"
    password = kwargs.get("password") if kwargs.get("password") else None
    port = kwargs.get("port") if kwargs.get("port") else 6379
    db_name = kwargs.get("db_name") if kwargs.get("db_name") else 0
    conn = Redis(host=host, port=port, db=db_name, password=password)
    return conn


def exist_in_dup(**kwargs):
    conn = connect_redis(**kwargs)
    task_url = kwargs.get("task_url")
    task_id = hashlib.md5(task_url.encode("utf-8")).hexdigest()
    print(conn.sismember('dup', task_id))


def exist_task(**kwargs):
    conn = connect_redis(**kwargs)
    task_url = kwargs.get("task_url")
    task_id = hashlib.md5(task_url.encode("utf-8")).hexdigest()
    if conn.exists(task_id):
        print(True)
    else:
        print(False)


def exist_in_temp_dup(**kwargs):
    conn = connect_redis(**kwargs)
    task_url = kwargs.get("task_url")
    sub_url = kwargs.get("sub_url")
    task_id = hashlib.md5(task_url.encode("utf-8")).hexdigest()
    sub_id = hashlib.md5(sub_url.encode("utf-8")).hexdigest()
    if conn.sismember(task_id, sub_id):
        print(True)
    else:
        print(False)


def delete_temp_dup(**kwargs):
    conn = connect_redis(**kwargs)
    task_url = kwargs.get("task_url")
    task_id = hashlib.md5(task_url.encode("utf-8")).hexdigest()
    if conn.delete(task_id):
        print(True)
    else:
        print(False)
