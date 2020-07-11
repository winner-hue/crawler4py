import hashlib
import os
from urllib.parse import urlparse, urljoin

from dispatch.starter import Starter
from setting import setting

start = Starter.get_instance("https://www.baidu.com", **setting)
start.start()
# import tldextract
#
# domain = tldextract.extract("https://www.baidu.com").registered_domain.replace(".", "_") + ".py"
#
# z = os.walk(os.path.join(os.path.dirname(__file__), "plugins", "download", "1"))
# print(os.path.join(os.path.dirname(__file__), "plugins", "download", "1"))
# for root, files, names in z:
#     if domain in names:
#         pass
