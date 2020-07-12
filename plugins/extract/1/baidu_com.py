from extractor.base_extract import BaseExtract
from log import Logger


class BaiDu(BaseExtract):
    def __init__(self, message):
        super(BaiDu, self).__init__(message)

    def process(self):
        Logger.logger.info("这是正确的哈")
        return self.message
