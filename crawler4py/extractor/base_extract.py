import re
from urllib.parse import urlparse, urljoin

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

    def process(self):
        task_url = self.message.get("task_url")
        parse = urlparse(task_url)
        scheme = parse.scheme
        netloc = parse.netloc
        host = "{}://{}/".format(scheme, netloc)
        self.message["next_pages"] = self.next_pages(host, netloc)

        for detail in self.re_detail:
            if re.search(detail, task_url):
                view_source = self.message.get("view_source")
                extractor = self.get_extractor(view_source, host=host)
                self.message["extract"] = extractor
                del self.message["next_pages"]  # 详细页面删掉下一页链接
                return self.message
        return self.message

    def get_extractor(self, view_source, host):
        extractor = GeneralNewsExtractor()
        extractor = extractor.extract(view_source, host=host)
        return extractor

    def next_pages(self, url_format, netloc):
        """
        获取下一页
        :param url_format:
        :param netloc:
        :return:
        """
        urls = []
        a_list = self.bf.find_all("a")
        for a in a_list:
            if not a:
                continue
            try:
                a = a.attrs["href"]
            except KeyError:
                continue

            a = a.split("#")[0]
            if a.__contains__("javascript"):
                continue
            if a.__contains__("@"):
                continue
            url = urljoin(url_format, a)
            if netloc.__eq__(urlparse(url).netloc):
                url_next = dict()
                url_next["url"] = url
                url_next["is_detail"] = False
                for detail in self.re_detail:
                    if re.search(detail, url):
                        url_next["is_detail"] = True
                        urls.append(url_next)
                        break
        return urls
