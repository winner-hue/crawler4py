import datetime
import os
from urllib.parse import urlparse

from log import Logger
from util.rabbitmqutil import get_data


@get_data
def call_back(ch, method, properties, body, **kwargs):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    message: dict = eval(body.decode())
    task_url = message.get("task_url")
    task_type = message.get("task_type")
    path = kwargs.get("plugins").get("download")
    if os.path.exists(f"{path}{os.sep}{task_type}"):
        pass

    Logger.logger.info(type(message))
