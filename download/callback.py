import datetime
from urllib.parse import urlparse

from log import Logger
from util.rabbitmqutil import get_data


@get_data
def call_back(ch, method, properties, body, **kwargs):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    message: dict = eval(body.decode())
    task_url = message.get("task_url")
    urlparse
    Logger.logger.info(type(message))
