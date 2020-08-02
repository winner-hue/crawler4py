import argparse
import hashlib
from datetime import datetime

import pymysql

parser = argparse.ArgumentParser(description="-- crawler4py commandline --")


def create_db(*args, **kwargs):
    print(args)
    print(kwargs)


def add_task(**kwargs):
    host = kwargs.get("host") if kwargs.get("host") else "127.0.0.1"
    user = kwargs.get("user") if kwargs.get("user") else "crawler4py"
    password = kwargs.get("password") if kwargs.get("password") else "crawler4py"
    database = kwargs.get("database") if kwargs.get("database") else "crawler4py"
    port = kwargs.get("port") if kwargs.get("port") else 3306
    conn = pymysql.connect(host=host, user=user, password=password, database=database, port=port)
    cursor = conn.cursor()

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


sql = parser.add_argument_group("-- sql commandline --")
sql.add_argument("--create_db", "-cdb", dest="create_db", action="store_const", const=create_db, help="创建数据库")
sql.add_argument("--add_task", "-at", dest="add_task", action="store_const", const=add_task, help="添加任务")

sql.add_argument("--task_url", "-tu", help="任务url")
sql.add_argument("--task_cell", "-tc", help="任务时间间隔")
sql.add_argument("--exec_time", "-et", help="任务执行时间")
sql.add_argument("--task_type", "-tt", help="任务类型")
sql.add_argument("--task_encode", "-te", help="页面编码")

args = parser.parse_args()


def main():
    args.add_task(task_url=args.task_url, task_cell=args.task_cell, exec_time=args.exec_time, task_type=args.task_type,
                  task_encode=args.task_encode)


if __name__ == '__main__':
    main()
