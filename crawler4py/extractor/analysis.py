import inspect
import os
import re

import tldextract

from crawler4py.extractor.base_extract import BaseExtract
from crawler4py.log import Logger


def process(message, path):
    task_type = message.get("task_type")
    task_url = message.get("task_url")
    plugin = get_plugin(task_url, task_type, path)
    if plugin:
        result = get_class(plugin, task_url, message).process()
    else:
        result = BaseExtract(message).process()
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


def get_class(task_plugin, task_url, message):
    """
    匹配插件
    :param task_plugin:
    :param task_url:
    :param message:
    :return:
    """
    for name, obj in inspect.getmembers(task_plugin):
        if inspect.isclass(obj):
            plugin_class = obj(message)
            for match in plugin_class.re_match:
                re_result = re.match(match, task_url)
                if re_result:
                    if hasattr(obj, 'process'):
                        return plugin_class
                    break
            else:
                continue
            del plugin_class
        else:
            continue
        break


def get_path(task_type, path):
    if task_type:
        new_path = path + "." + str(task_type)
    else:
        new_path = path
    return new_path
