from __future__ import division
import Tkinter as tk
import ttk
import os
from random import shuffle
import ConfigParser
import re
import logging
import collections
import time
import sys
import traceback
import StringIO

from PIL import Image
from PIL import ImageTk
import pyglet


def handleExceptions():
    # with thanks to Brad Barrows:
    # http://stackoverflow.com/questions/1508467/how-to-log-my-traceback-error
    old_print_exception = traceback.print_exception

    def custom_print_exception(etype, value, tb, limit=None, files=None):
        tb_output = traceback.format_exception(etype, value, tb)
        tb_output = list("\n") + tb_output
        fullException = "\n".join(tb_output)
        log.error(fullException)
        log.info('DevilScreens crashed at ' + time.strftime("%c"))
        sys.exit(1)

    traceback.print_exception = custom_print_exception


def silenceErr():
    def write(self, s):
        pass


class usableScreen:
    def __init__(self, Win32Display):
        self.x = Win32Display.x
        self.y = Win32Display.y
        self.w = Win32Display.width
        self.h = Win32Display.height
        if self.x < 0:
            self.setPos(0.95, "left", '+')
        if self.x > 0:
            self.setPos(0.05, "right", '')
        if self.x == 0:
            self.setPos(0.5, "center", '')
        self.dimensions = (self.w, self.h, self.gSign, self.x, self.y,)
        self.pw = self.w / 2
        self.ph = self.h / 2
        self.t = int(self.h * 0.05)
        self.b = int(self.h * 0.95)
        self.l = int(self.w * 0.05)
        self.r = int(self.w * 0.95)

    def setPos(self, percent, pos, string):
        self.cPos = int(self.w * percent)
        self.layoutPos = pos
        self.gSign = string


class imageList(object):
    def __init__(self, parent, data):
        self.parent = parent
        self.intervalTime = self.parent.interval
        self.files = wrappingList(data)
        self.loadedIndex = tk.IntVar()
        self.loadedIndex.set(0)
        self.historyArray = collections.deque()
        for x in range(-20, 20):
            self.historyArray.append(imageObject(self.files[x]))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, item):
        return self.historyArray[item % len(self.historyArray)]

    def passer(self):
        pass

    def nextImage(self):
        self.loadedIndex.set(self.loadedIndex.get() + 1)
        self.historyArray.popleft()
        self.historyArray.append(
            imageObject(self.files[self.loadedIndex.get() + 20]))
        self.updateActiveImage("next")

    def prevImage(self):
        self.loadedIndex.set(self.loadedIndex.get() - 1)
        self.historyArray.pop()
        self.historyArray.appendleft(
            imageObject(self.files[self.loadedIndex.get() - 20]))
        self.updateActiveImage("prev")

    def updateActiveImage(self, calledFromButton):
        self.actImg = self.historyArray[0]
        w, h = self.parent.m.w, self.parent.m.h
        iw, ih = self.actImg.image.size
        ratio = min(w / iw, h / ih)
        size = int(iw * ratio), int(ih * ratio)
        self.actImg.image = self.actImg.image.resize(size,
                                                     resample=Image.BICUBIC)
        self.showImage(calledFromButton)

    def showImage(self, calledFromButton):
        self.parent.p.displayimg = ImageTk.PhotoImage(
            self.actImg.image)
        self.parent.p.itemconfig(self.parent.p.show,
                                 image=self.parent.p.displayimg)
        self.parent.artist.set(self.actImg.artist)
        if self.parent.artist.get() == "":
            self.parent.p.itemconfig(self.parent.p.artistWindow,
                                     state="hidden")
        else:
            self.parent.p.itemconfig(self.parent.p.artistWindow,
                                     state="normal")
        if self.parent.running.get():
            func = self.nextImage
        else:
            func = self.passer
        self.parent.nextAlarm = self.parent.after(self.intervalTime, func)


class wrappingList(collections.Sequence):
    def __init__(self, data):
        self.list = list(data)

    def __len__(self):
        return len(self.list)

    def __getitem__(self, item):
        return self.list[item % len(self.list)]

    def __setitem__(self, key, value):
        self.list[key % len(self.list[:])] = value

    def __iter__(self):
        raise TypeError('cannot iterate infinite list!')


class imageObject(object):
    def __init__(self, ordFName):
        self.ordFName = ordFName
        self.ordName, self.ext = os.path.splitext(ordFName)
        self.creation = self.ordName[:20]
        self.fileHash = self.ordName[-64:]
        try:
            self.image = Image.open(ordFName)
        except Exception, e:
            logging.exception(e)
        try:
            self.artist = re.search('__(.+?)__', self.ordName).group(1)
            self.artist = re.sub(',', ' /', self.artist)
        except AttributeError:
            self.artist = ""

    def examine(self):
        for each in vars(self):
            print each + " : " + vars(self)[each]


class ssRoot(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.childWindows = 0
        self.baseDir = os.getcwdu()
        self.totalImages = tk.IntVar()
        self.totalImages.set(0)
        self.initialize()

    def initialize(self):
        self.config = ConfigParser.ConfigParser()
        self.readConfig()
        log.info("Folder = " + self.folder)
        log.info("Interval = " + str(self.interval))
        self.initDisplays()
        self.setupShuffledList()
        self.startShow()

    def readConfig(self):
        if os.path.exists("slideshow.ini"):
            self.config.read("slideshow.ini")
            self.displaysToUse = self.config.get('Config', 'monitors')
            self.displaysToUse = self.displaysToUse.split(',')
            self.displaysToUse = map(int, self.displaysToUse)
            self.numberOfMonitors = len(self.displaysToUse)
            self.interval = self.config.getint('Config', 'interval')
            self.folder = self.config.get('Config', 'folder')
            self.debugIndex = self.config.getboolean('Debug', 'index display')
        else:
            self.writeConfig()
            self.readConfig()

    def writeConfig(self):
        self.config.add_section('Config')
        self.config.set('Config', 'interval', '16000')
        self.config.set('Config', 'folder', os.getcwdu())
        self.config.set('Config', 'monitors', "0,1")
        self.config.add_section('Debug')
        self.config.set('Debug', 'index display', 'false')
        with open('slideshow.ini', 'wb') as configfile:
            self.config.write(configfile)

    def startShow(self):
        self.offsetCount = 0
        self.displaysUsed = list()
        self.displayId = 0
        for count, each in enumerate(self.displaysToUse):
            offset = int(self.startingOffset * self.displayId)
            self.displaysUsed.append(slideShowWindow(self, self.monitors[
                each], self.imageListArray[count], self.interval, offset))
            self.displayId += 1

    def setupShuffledList(self):
        pImgList = list()
        os.chdir(self.folder)
        self.uniSource = os.getcwdu()
        for fname in os.listdir(self.uniSource):
            path = os.path.join(self.uniSource, fname)
            if os.path.isdir(path):
                continue
            if fname.endswith(('.jpg', '.png', '.jpeg', '.gif')):
                pImgList.append(fname)
        shuffle(pImgList)
        self.imageListArray = list()
        for i in xrange(0, len(pImgList),
                        int(len(pImgList) / self.numberOfMonitors)):
            self.imageListArray.append(pImgList[i:i + (
                int(len(pImgList) / self.numberOfMonitors))])

    def initDisplays(self):
        self.display = pyglet.window.get_platform().get_default_display()
        monlist = self.display.get_screens()
        self.monitors = list()
        for each in monlist:
            self.monitors.append(usableScreen(each))
        self.startingOffset = self.interval / len(self.displaysToUse)


class slideShowWindow(tk.Toplevel):
    def __init__(self, parent, monitor, imagelist, interval, offset):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.m = monitor
        self.offset = offset
        self.interval = interval
        self.il = imageList(self, imagelist)
        self.artist = tk.StringVar()
        self.artist.set(None)
        self.running = tk.BooleanVar()
        self.running.set(False)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure(background='black')
        self.overrideredirect(1)
        self.geometry("%dx%d%s%+d%+d" % self.m.dimensions)
        self.makePanel()
        self.bind('<Key-Escape>', self.closeWindow)
        self.p.bind('<Enter>', self.showButtons)
        self.p.bind('<Leave>', self.hideButtons)
        self.p.tag_bind("open", "<ButtonPress-1>", self.openExternal)
        self.parent.childWindows += 1

    def makePanel(self):
        self.p = tk.Canvas(self, bd=0, highlightthickness=0)
        self.p.pack(fill="both", expand=1)
        self.p.configure(background='black')
        self.p.imagetoshow = None
        self.p.show = self.p.create_image(self.m.pw, self.m.ph,
                                          image=self.p.imagetoshow,
                                          anchor="center", tags="IMG")
        if self.parent.debugIndex is True:
            self.label = tk.Label(self.p, textvariable=self.il.loadedIndex,
                                  font=("Calibri", "36"), background="white")
            self.p.create_window(self.m.pw, self.m.ph, window=self.label)
        self.artistLabel = tk.Label(self.p, textvariable=self.artist,
                                    font=("Calibri", "16"), fg="white",
                                    background="black")
        self.p.artistWindow = self.p.create_window(self.m.pw, self.m.h,
                                                   anchor="s",
                                                   window=self.artistLabel)
        self.nextButton = ttk.Button(self.p, text=">", command=self.nextImage)
        self.prevButton = ttk.Button(self.p, text="<", command=self.prevImage)
        self.pauseButton = ttk.Button(self.p, textvariable=self.running,
                                      command=self.pauseUnpause)
        self.shareImg = ImageTk.PhotoImage(
            Image.open(os.path.join(self.parent.baseDir + '/icons/share.png')))
        self.nextAlarm = self.after(self.offset, self.il.updateActiveImage,
                                    False)
        self.running.set(True)

    def closeWindow(self, event):
        self.parent.totalImages.set(self.parent.totalImages.get() +
                                    self.il.loadedIndex.get())
        if self.parent.childWindows == 1:
            self.parent.destroy()
        else:
            self.parent.childWindows -= 1
            self.destroy()

    def showButtons(self, event):
        self.openButton = self.p.create_image(self.m.cPos, self.m.t,
                                              image=self.shareImg,
                                              anchor="center", tags=("open",
                                                                     "button",))
        self.p.create_window(self.m.r, self.m.ph, window=self.nextButton,
                             tags="button")
        self.p.create_window(self.m.cPos, self.m.b, window=self.pauseButton,
                             tags="button")
        self.p.create_window(self.m.l, self.m.ph, window=self.prevButton,
                             tags="button")

    def hideButtons(self, event):
        self.p.delete("button")

    def prevImage(self):
        self.after_cancel(self.nextAlarm)
        self.il.prevImage()

    def nextImage(self):
        self.after_cancel(self.nextAlarm)
        self.il.nextImage()

    def pauseUnpause(self):
        if self.running.get() == "Running":
            self.after_cancel(self.nextAlarm)
            self.running.set(False)
            # unpause delay?
        else:
            self.running.set(True)
            self.il.updateActiveImage("unpause")

    def openExternal(self):
        os.startfile(self.il.actImg.ordFName)


handleExceptions()
logfilename = 'system.log'
log = logging.getLogger()
logging.basicConfig(filename=logfilename, level=logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
log.addHandler(handler)
log.info('DevilScreens started at ' + time.strftime("%c"))

root = ssRoot(None)
root.withdraw()

root.mainloop()

log.info('DevilScreens closed at ' + time.strftime("%c"))
log.info('Showed ' + str(root.totalImages.get()) + ' total images')
exit()
