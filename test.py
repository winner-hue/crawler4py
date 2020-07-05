import hashlib
from urllib.parse import urlparse, urljoin

from dispatch.starter import Starter
from setting import setting

start = Starter.get_instance("https://www.baidu.com", **setting)
start.start()


