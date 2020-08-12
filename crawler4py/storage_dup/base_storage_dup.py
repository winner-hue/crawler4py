import hashlib

from pymongo.errors import DuplicateKeyError

from crawler4py.log import Logger
from crawler4py.util.mongoutil import MongoUtil
from crawler4py.util.redisutil import RedisUtil


class BaseStorageDup(object):
    def __init__(self, message):
        super(BaseStorageDup, self).__init__()
        self.message = message
        self.re_match = ['http']

    def process(self):
        return self.default()

    def dup(self, task_id, next_pages_detail):
        for result in self.message.get("next_pages"):
            url_id = hashlib.md5(result.get("url").encode("utf-8")).hexdigest()
            if RedisUtil.monitor_is_exist(task_id) and \
                    not RedisUtil.is_exist(task_id, url_id) and \
                    not RedisUtil.is_contains(url_id):
                next_pages_detail.append(result)
                if result.get("is_detail"):
                    RedisUtil.monitor_insert(task_id, 10,
                                             hashlib.md5(result.get("url").encode("utf-8")).hexdigest())
                else:
                    RedisUtil.monitor_insert(task_id, 100,
                                             hashlib.md5(result.get("url").encode("utf-8")).hexdigest())
        return next_pages_detail

    def storage(self, task_url):
        key = hashlib.md5(task_url.encode("utf-8")).hexdigest()
        if not RedisUtil.is_contains(key):
            self.message["_id"] = key
            try:
                MongoUtil.insert_one(self.message)
                Logger.logger.info("---{}----入库成功".format(task_url))
                RedisUtil.insert(key)
                RedisUtil.monitor_insert(self.message.get("task_id"), 100, key)
            except DuplicateKeyError as e:
                Logger.logger.error("插入数据错误：{}".format(e.with_traceback(None)))

    def default(self):
        task_url = self.message.get("task_url")
        # 非详细页面， 判断是否需要下发
        if not self.message.get("is_detail"):
            next_pages_detail = []
            task_id = self.message.get("task_id")
            next_pages_detail = self.dup(task_id, next_pages_detail)
            self.message["next_pages"] = next_pages_detail
            return self.message
        # 详细页面进行入库， 并进入排重库
        else:
            self.storage(task_url)
