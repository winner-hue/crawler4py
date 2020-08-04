import os
import re

import tldextract

from crawler4py.download.request import request
from crawler4py.log import Logger


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
        try:
            plugins = os.listdir(path.replace(".", "/"))
        except FileNotFoundError as e:
            return plugin
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
    header = message.get("header")
    # 下载默认重试3次
    for i in range(3):
        try:
            if header:
                r = request.get(task_url, header)
            else:
                r = request.get(task_url)
            if r.status_code > 400:
                message["recovery_flag"] = message["recovery_flag"] + 1 if message["recovery_flag"] else 1
            else:
                if message.get("task_encode"):
                    message["view_source"] = r.content.decode(message.get("task_encode"))
                else:
                    try:
                        # 自动匹配页面编码格式进行解码
                        encoding = re.search("charset=([a-zA-Z1-9\-]+)", r.text).group(1)
                        message["view_source"] = r.content.decode(encoding, errors="ignore")
                    except AttributeError:
                        message["view_source"] = str(r.content, r.encoding, errors='ignore')
            return message
        except Exception as e:
            Logger.logger.error("---{}---下载失败， 当前下载次数{}: {}".format(task_url, i + 1, e.with_traceback(None)))
    message["recovery_flag"] = message.get("recovery_flag") + 1 if message.get("recovery_flag") else 1
    return message
