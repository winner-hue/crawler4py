import datetime
import os
from urllib.parse import urlparse, urljoin

import tldextract

from log import Logger
from util.rabbitmqutil import get_data


@get_data
def call_back(ch, method, properties, body, **kwargs):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    message: dict = eval(body.decode())
    task_url = message.get("task_url")
    task_type = message.get("task_type")
    try:
        get_plugin(task_url, task_type ** kwargs)
    except:
        pass

    Logger.logger.info(type(message))


def get_plugin(task_url, task_type, **kwargs):
    registered_domain = tldextract.extract("https://www.baidu.com").registered_domain.replace(".", "_") + ".py"
    fqdn_domain = tldextract.extract("https://www.baidu.com").fqdn.replace(".", "_") + ".py"
    path = kwargs.get("plugins").get("download")
    if os.path.exists(f"{path}{os.sep}{task_type}"):
        for root, _, names in os.walk(f"{path}{os.sep}{task_type}"):
            if fqdn_domain in names:
                __import__(urljoin(root, fqdn_domain).replace(os.sep, ".").replace(".py", ""))
