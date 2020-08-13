from crawler4py.download.base_download import BaseDownload


class Test(BaseDownload):
    def __init__(self, message):
        super(Test, self).__init__(message)
