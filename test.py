import datetime
import hashlib
import os
import re
import uuid
from urllib.parse import urlparse, urljoin

from bson import iteritems

from dispatch.starter import Starter
from download.request import request
from log import Logger
from setting import setting

# start = Starter.get_instance("https://www.baidu.com", **setting)
from util.redisutil import RedisUtil

start = Starter.get_instance(**setting)
start.start()

# Logger.get_instance(**setting)
# print(RedisUtil.get_instance(**setting).monitor_insert("f3829204e49cfe315ed26832fd3b6c0b", 1000,
#                                                        "0830e050f85a0f8aa76011ffbf040ede"))
# print(not 10)
# import tldextract
#
# domain = tldextract.extract("https://www.baidu.com").registered_domain.replace(".", "_") + ".py"
#
# z = os.walk(os.path.join(os.path.dirname(__file__), "plugins", "download", "1"))
# print(os.path.join(os.path.dirname(__file__), "plugins", "download", "1"))
# for root, files, names in z:
#     if domain in names:
#         pass

# print(urlparse("https://www.baidu.com"))
#
# print(urljoin("https://www.baidu.com", "https://www.sina.com.cn"))
# import datetime
#
# print(datetime.datetime.now() - datetime.timedelta(seconds=3600))
# import hashlib
#
# print(hashlib.md5("https://news.sina.com.cn/".encode("utf-8")).hexdigest())

# 备注一下，两个问题
# 第一个；多线程会存在chnnal已经关闭的情况， （目前可能是因为下载线程出现问题） 已解决
# 第二个：布隆过滤器排重有问题（不是布隆过滤器的问题，数据该排重的都有排掉）

# 新问题：
# 第一个：任务排重无法排掉，会一直出现重复key录入错误
# 第二个：任务全部排掉之后， 没有停掉任务

# 之前问题已经解决， 下面是新问题
# 目前问题是任务已经停止，但是还有大量detail_url未入库完

# import requests
# from faker import Faker
#
# fack = Faker("zh_CN")
#
# headers = {
#     'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
#     'Accept-Encoding': ', '.join(('gzip', 'deflate')),
#     'Accept': '*/*',
#     'Connection': 'keep-alive',
# }
#
# r = requests.get("https://news.sina.com.cn/", headers=headers)
# # print(r.content.decode("utf-8", errors="ignore"))
# print(r.content.decode(re.search("charset=([a-zA-Z1-9\-]+)", r.text).group(1), 'ignore'))
