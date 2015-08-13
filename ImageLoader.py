from __future__ import division
import multiprocessing
from Queue import Empty
from multiprocessing import Queue
from PIL import Image
import time
import os
import sys


# Thanks to @UdacityJeremy for the framework from which this file was made:
# https://github.com/UdacityJeremy/PooledImageloader

def size(image, w, h):
    nimage = image
    iw, ih = image.size
    ratio = min(w / iw, h / ih)
    size = int(iw * ratio), int(ih * ratio)
    # if ih < h:
    #     if iw < w:
    #         nimage = nimage.resize((int(x * 2) for x in size),
    #                              Image.NEAREST)
    # nimage.thumbnail(size, Image.ANTIALIAS)
    nimage = nimage.resize(size, Image.ANTIALIAS)
    return nimage


def worker_main(input_queue, output_queue):
    opentimer = set()
    resizetimer = set()
    count = 0
    while True:
        data = input_queue.get()
        path, w, h = data
        # if path.endswith('png'):
        #     print "resizing", path
        # with Timer() as t:
        image = Image.open(path)
        # if t.secs is not 0.0:
        #     opentimer.add(t.secs)
        # with Timer() as g:
        image = size(image, w, h)
        # if g.secs is not 0.0:
        #     resizetimer.add(g.secs)
        # count += 1
        # if count % 100 == 0:
        #     print "avg open: " + str(sum(opentimer) / len(opentimer))
        #     print "avg resize: " + str(sum(resizetimer) / len(resizetimer))
        image = {
            'pixels': image.tobytes(),
            'size': image.size,
            'mode': image.mode,
        }
        print path
        imobj = list((path, image))
        # if count % 100 == 0:
        #     print count
        output_queue.put(imobj)


class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print 'elapsed time: %f ms' % self.msecs


class ImageLoader:
    OUTPUT_QUEUE_SIZE = 1000
    INPUT_QUEUE_SIZE = 1000
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
            imobj = self.output_queue.get_nowait(*p, **kw)
            image = imobj[1]
            image = Image.frombytes(
                image['mode'],
                image['size'],
                image['pixels'])
            imobj[1] = image
            return imobj
        except Empty:
            e = sys.exc_info()[0]
            if e is not Empty:
                print e
            return "none"


def main():
    loader = ImageLoader()
    loader.start("E:/Dropbox/ordfaves")
    pImgList = list()
    os.chdir("E:/Dropbox/ordfaves")
    uniSource = os.getcwdu()
    for fname in os.listdir(uniSource):
        path = os.path.join(uniSource, fname)
        if os.path.isdir(path):
            continue
        if fname.endswith(('.jpg', '.png', '.jpeg', '.gif')):
            pImgList.append(fname)
    print "start"
    for each in pImgList:
        loader.put(each, 1680, 1050)
    print "all added"


if __name__ == '__main__':
    main()
