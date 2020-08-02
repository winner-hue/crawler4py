import pika

from crawler4py.log import Logger


def connect(queue_name, user, pwd, host, port, exchange=None, exchange_type=None):
    """
    连接rabbitmq
    :param queue_name:
    :param user:
    :param pwd:
    :param host:
    :param port:
    :param exchange:
    :param exchange_type:
    :return:
    """
    credentials = pika.PlainCredentials(user, pwd)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, port=port,
                                  virtual_host='crawler4py',
                                  credentials=credentials))
    channel = connection.channel()
    if exchange_type is None:
        channel.queue_declare(queue=queue_name, durable=True)
    else:
        channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=True)
        if not queue_name.__eq__(''):
            channel.queue_declare(queue=queue_name, durable=True)
            channel.queue_bind(exchange=exchange, queue=queue_name)
    return channel


def send_data(channel, exchange, message, routing_key):
    """
    向rabitmq中发送数据
    :param channel:
    :param exchange:
    :param message:
    :param routing_key:
    :return:
    """
    try:
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message,
                              properties=pika.BasicProperties(delivery_mode=2))
    except Exception as e:
        Logger.logger.info("数据发送失败： {}".format(e.with_traceback(None)))
        return False
    return True


def get_data(call_back):
    """
    回调函数
    :param call_back:
    :return:
    """

    def do_data(*args, **kwargs):
        """
        执行回调函数，获取数据
        :param args:
        :param kwargs:
        :return:
        """
        no_ack = kwargs.get("no_ack")
        channel = kwargs.get("channel")
        routing_key = kwargs.get("routing_key")
        # no_ack 是rabbitmq中用来判断是否保留任务，True为不保留， False为保留
        if no_ack is not None:
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(routing_key, call_back, no_ack=False)
        else:
            channel.basic_consume(routing_key, call_back)
        channel.start_consuming()

    return do_data


def get_queue(setting, queue_name):
    try:
        mq_queue = setting.get("mq_queue").get(queue_name)
        if not mq_queue:
            mq_queue = queue_name
    except AttributeError:
        mq_queue = queue_name

    return mq_queue


def get_login_info(setting):
    try:
        user = setting.get("mq").get("user")
        pwd = setting.get("mq").get("pwd")
        host = setting.get("mq").get("host")
        port = setting.get("mq").get("port")
        api_port = setting.get("mq").get("api_port")
    except AttributeError:
        user = "crawler4py"
        pwd = "crawler4py"
        host = "127.0.0.1"
        port = 5672
        api_port = 15672
    return user, pwd, host, port, api_port
