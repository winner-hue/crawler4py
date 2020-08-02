import re

from gne import GeneralNewsExtractor

from crawler4py.extractor.base_extract import BaseExtract


class BaiDu(BaseExtract):
    def __init__(self, message):
        super(BaiDu, self).__init__(message)
        # 用来匹配适合的插件类，用来解析匹配的页面
        self.re_match = ['https://news.163.com/']
        # 用来匹配需要抓取的页面
        self.re_detail = [r'/\d+-\d+-\d+/\w+']

    def get_extractor(self, view_source, host):
        extractor = GeneralNewsExtractor()
        extractor = extractor.extract(view_source, host=host)
        return extractor

    def next_pages(self, url_format, netloc):
        urls = []
        url_next = dict()
        url_next["url"] = "https://news.163.com"
        url_next["is_detail"] = False
        for detail in self.re_detail:
            if re.search(detail, "https://news.163.com"):
                url_next["is_detail"] = True
                urls.append(url_next)
                break
        return urls
