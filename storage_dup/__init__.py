from pycrawler import Crawler


class BaseStorageDup(Crawler):
    def start(self):
        pass

    def run(self):
        print("入库排重启动")
