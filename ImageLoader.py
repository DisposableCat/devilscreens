from __future__ import division
import multiprocessing
from Queue import Empty
from multiprocessing import Queue
from PIL import Image
import time
import os
import sys
import gc
import io


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
    while True:
        data = input_queue.get()
        iofile, w, h = data
        image = Image.open(iofile)
        # if path.endswith('png'):
        #     print "resizing", path
        with Timer() as g:
            image = size(image, w, h)
        resizetime = g.secs
        # image = {
        #     'pixels': image.tobytes(),
        #     'size': image.size,
        #     'mode': image.mode,
        # }
        # imobj = list((image))
        output_queue.put(resizetime)
        # output_queue.put(imobj)


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
        with Timer() as t:
            with open(filename, 'rb') as f:
                iofile = io.BytesIO(f.read())
        opentime = t.secs
        self.input_queue.put((iofile, w, h))
        return opentime

    def get(self, *p, **kw):
        try:
            imobj = self.output_queue.get_nowait(*p, **kw)
            # image = imobj[1]
            # image = Image.frombytes(
            #     image['mode'],
            #     image['size'],
            #     image['pixels'])
            # imobj[1] = image
            return imobj
        except Empty:
            e = sys.exc_info()[0]
            if e is not Empty:
                print e
            return "none"


def main():
    folder = "G:/pictures/stp/new"
    loader = ImageLoader()
    pImgList = list()
    loader.start(folder)
    os.chdir(folder)
    uniSource = os.getcwdu()
    for fname in os.listdir(uniSource):
        path = os.path.join(uniSource, fname)
        if os.path.isdir(path):
            continue
        if fname.endswith(('.jpg', '.png', '.jpeg', '.gif')):
            pImgList.append(fname)
    print "files: ", len(pImgList)
    print "start"
    count = 1
    opentimer = set()
    resizetimer = set()
    for each in pImgList:
        opentimer.add(loader.put(each, 1680, 1050))
        imgobj = loader.get()
        if imgobj is not "none":
            resizetimer.add(imgobj)
            count += 1
        if count % 10 == 0:
            print len(resizetimer)
            resavg = sum(resizetimer) / len(resizetimer)
            openavg = sum(opentimer) / len(opentimer)
            print "avg resize: ", str(resavg)
            print len(opentimer)
            print "avg open: ", str(openavg)
    print "done"


if __name__ == '__main__':
    main()
