import sys

from pycrawler import Crawler
from util.running_params import task_q


class Downloader(Crawler):

    def single(self):
        while True:
            task_url = task_q.get()
            print(task_url)
            single_over_signal = 1
            sys.exit(0)

    def run(self):
        print("下载启动")
        if not task_q.empty():
            self.single()
        else:
            pass
