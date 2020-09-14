import time

import tldextract

from crawler4py.download.request import request
from crawler4py.log import Logger


def get_plugin_path(setting, path):
    """
    获取插件位置
    :param setting: 
    :param path: 
    :return: 
    """
    try:
        path = setting.get("plugins").get(path)
    except AttributeError:
        path = None

    return path


def get_download_task_size_limit(setting):
    download_task_size_limit = setting.get(
        "download_task_size_limit") if setting.get("download_task_size_limit") else 500
    return download_task_size_limit


def is_send(mq_params, setting, mq_queue):
    while True:
        messages = request.get(
            "http://{}:{}/api/queues/crawler4py/{}/".format(mq_params[2], mq_params[4], mq_queue),
            auth=(mq_params[0], mq_params[1])).json().get("messages")

        if not messages:
            messages = 0

        size = get_download_task_size_limit(setting)
        if messages < size:
            Logger.logger.info("当前队列大小：{}".format(messages))
            break
        else:
            Logger.logger.info("下载队列任务数量超出限制，30秒后继续尝试下发")
            time.sleep(30)


def get_plugin(task_url, task_type, path):
    registered_domain = tldextract.extract(task_url).registered_domain.replace(".", "_") + ".py"
    fqdn_domain = tldextract.extract(task_url).fqdn.replace(".", "_") + ".py"
    plugin = None
    if path:
        path = get_path(task_type, path)
        plugin = find_plugin(plugin, path, fqdn_domain, registered_domain)
    return plugin


def find_plugin(plugin, path, fqdn_domain, registered_domain):
    try:
        try:
            plugin = __import__(path + "." + fqdn_domain.replace(".py", ""), globals(), locals(),
                                [fqdn_domain.replace(".py", "")])
        except:
            plugin = __import__(path + "." + registered_domain.replace(".py", ""), globals(), locals(),
                                [registered_domain.replace(".py", "")])
    except Exception as e:
        return plugin


def get_path(task_type, path):
    if task_type:
        new_path = path + "." + str(task_type)
    else:
        new_path = path
    return new_path
