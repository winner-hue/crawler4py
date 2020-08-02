from crawler4py.dispatch.starter import Starter
from crawler4py.setting import setting


def main():
    start = Starter.get_instance(**setting)
    start.start()


main()
