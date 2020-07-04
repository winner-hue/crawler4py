from util.rabbitmqutil import get_data


@get_data
def call_back(self, ch, method, properties, body, **kwargs):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    message = body.decode()
    print(message)
