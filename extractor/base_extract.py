from urllib.parse import urlparse

from bs4 import BeautifulSoup
from gne import GeneralNewsExtractor
from lxml import html


class BaseExtract(object):
    def __init__(self, message):
        super(BaseExtract, self).__init__()
        self.message = message
        view_source = message.get("view_source")
        self.bf = BeautifulSoup(view_source, "lxml")
        self.html = html.fromstring(view_source)
        # 用来匹配适合的插件类，用来解析匹配的页面
        self.re_match = ['http']
        # 用来匹配需要抓取的页面
        self.re_detail = [r'/\d+-\d+-\d+/\w+']
        self.date_format = "%Y年%m月%d日 %H:%M:%S"

    def process(self):
        task_url = self.message.get("task_url")
        parse = urlparse(task_url)
        scheme = parse.scheme
        netloc = parse.netloc
        view_source = self.message.get("view_source")
        extractor = GeneralNewsExtractor()
        extractor = extractor.extract(view_source, host="{}://{}".format(scheme, netloc))
        self.message["extract"] = extractor
        return self.message
