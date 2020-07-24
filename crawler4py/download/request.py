from requests import Session
from faker import Faker
from requests.structures import CaseInsensitiveDict

fack = Faker("zh_CN")


class Request(Session):
    def __init__(self):
        super(Request, self).__init__()
        self.headers = default_headers()

    def download_pic(self):
        pass

    def post_pic(self):
        pass

    def download_video(self):
        pass

    def post_video(self):
        pass


def request():
    return Request()


def default_headers():
    return CaseInsensitiveDict({
        'User-Agent': fack.user_agent(),
        'Accept-Encoding': ', '.join(('gzip', 'deflate')),
        'Accept': '*/*',
        'Connection': 'keep-alive',
    })


request = request()
