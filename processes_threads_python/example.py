import logging
from multiprocessing import Process
from threading import Thread
import time


def foobar(identity):
    for i in range(1000):
        logging.info('I am {}'.format(identity))
        time.sleep(0.001)


def main():
    logging.basicConfig(level='INFO')

    t = Thread(target=foobar, args=('thread',))
    p = Process(target=foobar, args=('process',))

    t.start()
    p.start()

    t.join()
    logging.info('thread joined')

    p.join()
    logging.info('process joined')


if __name__ == '__main__':
    main()
