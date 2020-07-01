from log import Logger
from util.rabbitmqutil import get_data


@get_data
def call_back(ch, method, properties, body, **kwargs):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    message = body.decode()
    Logger.logger.info(message)
