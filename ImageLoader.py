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


def worker_main(input_queue, output_queue, testing):
    while True:
        data = input_queue.get()
        iofile, filename, w, h = data
        image = Image.open(iofile)
        if testing:
            with Timer() as g:
                image = size(image, w, h)
            resizetime = g.secs
            del image
            output_queue.put(resizetime)
        if not testing:
            image = size(image, w, h)
            image = {
                'pixels': image.tobytes(),
                'size': image.size,
                'mode': image.mode,
            }
            imobj = list((filename, image))
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
    global testing
    OUTPUT_QUEUE_SIZE = 1000
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
                                             testing
                                         ))

    def stop(self):
        self.pool.terminate()

    def put(self, filename, w, h):
        if testing:
            with Timer() as t:
                with open(filename, 'rb') as f:
                    iofile = io.BytesIO(f.read())
            opentime = t.secs
            self.input_queue.put((iofile, filename, w, h))
            return opentime
        if not testing:
            with open(filename, 'rb') as f:
                iofile = io.BytesIO(f.read())
            self.input_queue.put((iofile, filename, w, h))

    def get(self, *p, **kw):
        try:
            imobj = self.output_queue.get_nowait(*p, **kw)
            if not testing:
                image = imobj[1]
                image = Image.frombytes(
                    image['mode'],
                    image['size'],
                    image['pixels'])
                imobj[1] = image
                print self.output_queue.qsize()
            return imobj
        except Empty:
            e = sys.exc_info()[0]
            if e is not Empty:
                print e
            return "none"


def main():
    global testing
    print testing
    folder = "C:/Users/Fenrir/Pictures/worksafe wallpapers"
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
    opentimer = list()
    resizetimer = list()
    for each in pImgList:
        opener = loader.put(each, 1680, 1050)
        opentimer.append(opener)
        imgobj = loader.get()
        if imgobj is not "none":
            resizetimer.append(imgobj)
            count += 1
        if count % 100 == 0:
            print len(resizetimer), "resizes"
            resavg = sum(resizetimer) / len(resizetimer)
            openavg = sum(opentimer) / len(opentimer)
            print "avg resize: ", str(resavg)
            print len(opentimer), "opens"
            print "avg open: ", str(openavg)
    print "done"


testing = False

if __name__ == '__main__':
    testing = True
    main()
