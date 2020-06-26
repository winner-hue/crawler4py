from dispatch.dispatch import Dispatch
from downloader.downloader import Downloader
from extractor.extractor import Extractor
from storage_dup import BaseStorageDup

'''启动器'''


class Starter(object):
    def __init__(self, url, **setting):
        super(Starter, self).__init__()
        self.url = url
        self.setting = setting
        self.dispatch_thread_size = setting.get("dispatch_thread_size") if setting.get(
            "dispatch_thread_size") else 1
        self.downloader_thread_size = setting.get("downloader_thread_size") if setting.get(
            "downloader_thread_size") else 10
        self.extractor_thread_size = setting.get("extractor_thread_size") if setting.get(
            "extractor_thread_size") else 5
        self.storage_dup_thread_size = setting.get("storage_dup_thread_size") if setting.get(
            "storage_dup_thread_size") else 2

    def start(self):
        crawler = Dispatch(**self.setting)
        crawler.start_url = self.url
        self.install(crawler)
        crawler.start()

    def install(self, crawler: Dispatch):
        for i in range(self.dispatch_thread_size):
            crawler.installed(Dispatch(**self.setting), 1)
        for i in range(self.downloader_thread_size):
            crawler.installed(Downloader(**self.setting), 2)
        for i in range(self.extractor_thread_size):
            crawler.installed(Extractor(**self.setting), 3)
        for i in range(self.storage_dup_thread_size):
            crawler.installed(BaseStorageDup(**self.setting), 4)
