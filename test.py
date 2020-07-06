import hashlib
import os
from urllib.parse import urlparse, urljoin

from dispatch.starter import Starter
from setting import setting

# start = Starter.get_instance("https://www.baidu.com", **setting)
# start.start()


z = os.walk("./dispatch")
for root, _, names in z:
    for name in names:
        print(os.path.join(root, name))

