import inspect
import re

from crawler4py.extractor.base_extract import BaseExtract
from crawler4py.util.commonutil import get_plugin


def process(message, path):
    task_type = message.get("task_type")
    task_url = message.get("task_url")
    plugin = get_plugin(task_url, task_type, path)
    if plugin:
        plugin_class = get_class(plugin, task_url, message)
        result = plugin_class.process()
    else:
        plugin_class = BaseExtract(message)
        result = plugin_class.process()
    del plugin_class
    return result


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
