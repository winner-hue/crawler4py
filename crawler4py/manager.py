import argparse
import sys

sys.path.append("..")

from crawler4py.command import *

parser = argparse.ArgumentParser(description="-- crawler4py commandline --")

parser.add_argument("--task_url", "-tu", help="任务url")
parser.add_argument("--sub_url", "-su", help="子任务url")
parser.add_argument("--task_cell", "-tc", help="任务时间间隔")
parser.add_argument("--exec_time", "-et", help="任务执行时间")
parser.add_argument("--task_type", "-tt", help="任务类型")
parser.add_argument("--task_encode", "-te", help="页面编码")
parser.add_argument("--host", help="数据库主机地址")
parser.add_argument("--port", "-P", help="数据库端口")
parser.add_argument("--user", "-u", help="数据库用户名")
parser.add_argument("--password", "-p", help="数据库密码")
parser.add_argument("--db_name", "-dn", help="数据库名称")

sql = parser.add_argument_group("sql commandline")
sql.add_argument("--create_db", "-cdb", dest="create_db", action="store_const", const=create_db, help="创建数据库")
sql.add_argument("--drop_db", "-ddb", dest="drop_db", action="store_const", const=drop_db, help="删除数据库")
sql.add_argument("--add_task", "-at", dest="add_task", action="store_const", const=add_task, help="添加任务")
sql.add_argument("--delete_task", "-dt", dest="delete_task", action="store_const", const=delete_task, help="删除任务")
sql.add_argument("--create_table", "-ctb", dest="create_table", action="store_const", const=create_table, help="创建表")

no_sql = parser.add_argument_group("no_sql commandline")
no_sql.add_argument("--exist_in_dup", "-eid", dest="exist_in_dup", action="store_const", const=exist_in_dup,
                    help="判断url是否已经在排重库")
no_sql.add_argument("--exist_task", "-eit", dest="exist_task", action="store_const", const=exist_task,
                    help="判断是否存在该任务")
no_sql.add_argument("--exist_in_temp_dup", "-eitd", dest="exist_in_temp_dup", action="store_const",
                    const=exist_in_temp_dup,
                    help="判断url是否已经在排重库")
no_sql.add_argument("--delete_temp_dup", "-dtd", dest="delete_temp_dup", action="store_const", const=delete_temp_dup,
                    help="判断url是否已经在排重库")

args = parser.parse_args()


def main():
    if args.add_task:
        args.add_task(task_url=args.task_url, task_cell=args.task_cell, exec_time=args.exec_time,
                      task_type=args.task_type, task_encode=args.task_encode, host=args.host, port=args.port,
                      user=args.user, password=args.password, db_name=args.db_name)
    if args.delete_task:
        args.delete_task(host=args.host, port=args.port, user=args.user, password=args.password, db_name=args.db_name,
                         task_url=args.task_url)
    if args.create_db:
        args.create_db(host=args.host, port=args.port, user=args.user, password=args.password, db_name=args.db_name)
    if args.drop_db:
        args.drop_db(host=args.host, port=args.port, user=args.user, password=args.password, db_name=args.db_name)
    if args.exist_in_dup:
        args.exist_in_dup(task_url=args.task_url, host=args.host, port=args.port, password=args.password,
                          db_name=args.db_name)
    if args.exist_task:
        args.exist_task(task_url=args.task_url, host=args.host, port=args.port, password=args.password,
                        db_name=args.db_name)
    if args.delete_temp_dup:
        args.delete_temp_dup(task_url=args.task_url, host=args.host, port=args.port, password=args.password,
                             db_name=args.db_name)
    if args.exist_in_temp_dup:
        args.exist_in_temp_dup(task_url=args.task_url, sub_url=args.sub_url, host=args.host, port=args.port,
                               password=args.password,
                               db_name=args.db_name)
    if args.create_table:
        args.create_table(host=args.host, port=args.port, user=args.user, password=args.password, db_name=args.db_name)


if __name__ == '__main__':
    main()
