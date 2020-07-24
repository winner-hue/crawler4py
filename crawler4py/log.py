import json
import logging
import logging.config

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(lineno)d  %(asctime)s %(threadName)s--%(filename)s--%(funcName)s--%(levelname)s--%(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "py_crawler": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": "no"
        }
    }
}


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
                config = log_config
            logging.config.dictConfig(config)
            Logger.logger = logging.getLogger("py_crawler")
            Logger.logger.info("日志实例化成功")
            cls.__instance = Logger()
        return cls.__instance
