from dispatch.starter import Starter
from setting import setting


start = Starter("https://www.baidu.com", **setting)

start.start()