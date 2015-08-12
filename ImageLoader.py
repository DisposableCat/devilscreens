from __future__ import division
import multiprocessing
from multiprocessing import Queue
from PIL import Image
import time
import os


# Thanks to @UdacityJeremy for the framework from which this file was made:
# https://github.com/UdacityJeremy/PooledImageloader

def worker_main(input_queue, output_queue):
    while True:
        data = input_queue.get()
        path, w, h = data
        image = Image.open(path)
        iw, ih = image.size
        ratio = min(w / iw, h / ih)
        size = int(iw * ratio), int(ih * ratio)
        image = image.resize(size, Image.BICUBIC)
        imobj = (path, image)
        output_queue.put(imobj)


class ImageLoader:
    OUTPUT_QUEUE_SIZE = 100
    INPUT_QUEUE_SIZE = 100
    WORKER_COUNT = 3

    def __init__(self):
        self.input_queue = Queue(self.INPUT_QUEUE_SIZE)
        self.output_queue = Queue(self.OUTPUT_QUEUE_SIZE)

    def start(self, folder):
        os.chdir(folder)
        self.pool = multiprocessing.Pool(self.WORKER_COUNT,
                                         worker_main, (
                                             self.input_queue,
                                             self.output_queue,
                                         ))

    def stop(self):
        self.pool.terminate()

    def put(self, filename, w, h):
        self.input_queue.put((filename, w, h))

    def get(self, *p, **kw):
        try:
            return self.output_queue.get_nowait(*p, **kw)
        except:
            pass


def main():
    loader = ImageLoader("../testImages")
    loader.start()
    time.sleep(3)
    for x in range(2000):
        time.sleep(1)
        thing = loader.get(False)
        print "got a thing", thing


if __name__ == '__main__':
    main()
