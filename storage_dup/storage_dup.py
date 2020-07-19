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
    if message.get("next_pages"):
        next_pages_detail = []
        task_id = message.get("task_id")
        for result in message.get("next_pages"):
            url_id = hashlib.md5(result.get("url").encode("utf-8")).hexdigest()
            if RedisUtil.monitor_is_exist(task_id) and \
                    not RedisUtil.is_exist(task_id, url_id) and \
                    not RedisUtil.is_contains(url_id):
                next_pages_detail.append(result)
                RedisUtil.monitor_insert(task_id, hashlib.md5(result.get("url").encode("utf-8")).hexdigest())

        message["next_pages"] = next_pages_detail
        return message

    key = hashlib.md5(task_url.encode("utf-8")).hexdigest()
    if not RedisUtil.is_contains(key):
        message["_id"] = key
        try:
            MongoUtil.insert_one(message)
            Logger.logger.info("---{}----入库成功".format(message.get("task_url")))
            RedisUtil.insert(key)
        except DuplicateKeyError as e:
            Logger.logger.error("插入数据错误：{}".format(e))
