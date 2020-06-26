from pycrawler import Crawler


class Dispatch(Crawler):

    def start(self):
        print(self.start_url)
