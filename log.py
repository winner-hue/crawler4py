import json
import logging
import logging.config
import os


class Logger(object):
    __instance = None
    logger: logging.Logger = None

    @classmethod
    def get_instance(cls, **setting):
        if not cls.__instance:
            if setting.get("logger_path"):
                with open(setting.get("logger_path"), "r", encoding="utf-8") as f:
                    config = json.load(f)
            else:
                with open("logging.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
            logging.config.dictConfig(config)
            Logger.logger = logging.getLogger("py_crawler")
            Logger.logger.info("日志实例化成功")
            cls.__instance = Logger()
        return cls.__instance
