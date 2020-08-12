import re

from crawler4py.crawler import Crawler
from crawler4py.download.request import request
from crawler4py.log import Logger


class BaseDownload(object):
    def __init__(self, message):
        super(BaseDownload, self).__init__()
        self.message = message
        self.re_match = ['http']
        self.download_again = Crawler.crawler_setting.get("download_again") if Crawler.crawler_setting.get(
            "download_again") else 3

    def process(self):
        return self.default()

    def mark_flag(self):
        self.message["recovery_flag"] = self.message["recovery_flag"] + 1 if self.message[
            "recovery_flag"] else 1

    def default_download(self, header, task_url):
        if header:
            r = request.get(task_url, header)
        else:
            r = request.get(task_url)
        return r

    def get_view_source(self, r):
        if self.message.get("task_encode"):
            self.message["view_source"] = r.content.decode(self.message.get("task_encode"))
        else:
            try:
                # 自动匹配页面编码格式进行解码
                encoding = re.search("charset=([a-zA-Z1-9\-]+)", r.text).group(1)
                self.message["view_source"] = r.content.decode(encoding, errors="ignore")
            except AttributeError:
                self.message["view_source"] = str(r.content, r.encoding, errors='ignore')

    def default(self):
        task_url = self.message.get("task_url")
        header = self.message.get("header")
        # 下载默认重试3次
        for i in range(self.download_again):
            try:
                r = self.default_download(header, task_url)
                if r.status_code > 400:
                    self.mark_flag()
                else:
                    self.get_view_source(r)
                return self.message
            except Exception as e:
                Logger.logger.error("---{}---下载失败， 当前下载次数{}: {}".format(task_url, i + 1, e.with_traceback(None)))
                self.mark_flag()
        return self.message
