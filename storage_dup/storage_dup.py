import hashlib
import os

import tldextract
from pymongo.errors import DuplicateKeyError

from log import Logger
from util.mongoutil import MongoUtil
from util.redisutil import RedisUtil


def process(message, path):
    task_type = message.get("task_type")
    task_url = message.get("task_url")
    plugin = get_plugin(task_url, task_type, path)
    if plugin:
        result = plugin.process(task_url, message)
    else:
        result = default(task_url, message)
    return result


def get_plugin(task_url, task_type, path):
    registered_domain = tldextract.extract(task_url).registered_domain.replace(".", "_") + ".py"
    fqdn_domain = tldextract.extract(task_url).fqdn.replace(".", "_") + ".py"
    plugin = None
    if path:
        path = get_path(task_type, path)
        plugins = os.listdir(path.replace(".", "/"))
        if fqdn_domain in plugins:
            plugin = __import__(path + "." + fqdn_domain.replace(".py", ""), globals(), locals(),
                                [fqdn_domain.replace(".py", "")])
        if registered_domain in plugins:
            plugin = __import__(path + "." + registered_domain.replace(".py", ""), globals(), locals(),
                                [registered_domain.replace(".py", "")])

    return plugin


def get_path(task_type, path):
    if task_type:
        new_path = path + "." + str(task_type)
    else:
        new_path = path
    return new_path


def default(task_url, message):
    key = hashlib.md5(task_url.encode("utf-8")).hexdigest()
    if message.get("next_pages"):
        next_pages = [result for result in message.get("next_pages") if
                      result.get("is_detail") and not RedisUtil.is_contains(key)]
        if len(next_pages) == 0:
            message["next_pages"] = []
            return message
        new_next_pages = []
        for result in next_pages:
            url_key = hashlib.md5(result.get("url").encode("utf-8")).hexdigest()
            if RedisUtil.monitor_insert(message.get("task_id"), url_key):
                new_next_pages.append(result)
        del next_pages
        new_next_pages.extend([result for result in message.get("next_pages") if not result.get("is_detail")])
        message["next_pages"] = new_next_pages
        return message
    if not RedisUtil.is_contains(key):
        message["_id"] = key
        try:
            MongoUtil.insert_one(message)
        except DuplicateKeyError as e:
            Logger.logger.error("插入数据错误：{}".format(e))
        RedisUtil.insert(key)
        Logger.logger.info("---{}----入库成功".format(message.get("task_url")))
        RedisUtil.del_exist(message.get("task_id"), key)
