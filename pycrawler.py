class Crawler(object):
    crawler_setting = None

    def __init__(self, **setting: dict):
        Crawler.crawler_setting = setting
        if not setting:
            raise Exception("配置属性setting不能为空")

    @staticmethod
    def installed(obj, obj_list: list):
        obj_list.append(obj)

    def run(self):
        raise NotImplemented
