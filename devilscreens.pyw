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
    #with thanks to Brad Barrows:
    #http://stackoverflow.com/questions/1508467/how-to-log-my-traceback-error
    old_print_exception = traceback.print_exception
    def custom_print_exception(etype, value, tb, limit=None, file=None):
        tb_output = StringIO.StringIO()
        traceback.print_tb(tb, limit, tb_output)
        log.error(tb_output.getvalue())
        tb_output.close()
        log.info('DevilScreens crashed at ' + time.strftime("%c"))
        sys.exit(1)
    traceback.print_exception = custom_print_exception

def silenceErr():
    def write(self, s):
        pass

class imageList(object):
    def __init__(self, parent, data):
        self.parent = parent
        self.intervalTime = self.parent.interval
        self.filenames = wrappingList(data)
        self.loadedIndex = tk.IntVar()
        self.loadedIndex.set(0)
        self.historyArray = collections.deque()
        for x in range(-20, 20):
            self.historyArray.append(imageObject(self.filenames[x]))

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, item):
        return self.historyArray[item % len(self.historyArray)]

    def passer(self):
        pass

    def nextImage(self):
        self.loadedIndex.set(self.loadedIndex.get() + 1)
        self.historyArray.popleft()
        self.historyArray.append(
            imageObject(self.filenames[self.loadedIndex.get() + 20]))
        self.updateActiveImage("next")

    def prevImage(self):
        self.loadedIndex.set(self.loadedIndex.get() - 1)
        self.historyArray.pop()
        self.historyArray.appendleft(
            imageObject(self.filenames[self.loadedIndex.get() - 20]))
        self.updateActiveImage("prev")

    def updateActiveImage(self, calledFromButton):
        self.activeImage = self.historyArray[0]
        self.activeImage.w, self.activeImage.h = \
            self.parent.monitor.width, self.parent.monitor.height
        self.activeImage.iw, self.activeImage.ih = self.activeImage.image.size
        self.activeImage.ratio = min(self.activeImage.w / self.activeImage.iw,
                                     self.activeImage.h / self.activeImage.ih)
        self.activeImage.size = int(
            self.activeImage.iw * self.activeImage.ratio), int(
            self.activeImage.ih * self.activeImage.ratio)
        self.activeImage.resized = self.activeImage.image.resize(
            self.activeImage.size,
            resample=Image.BICUBIC)
        self.showImage(calledFromButton)

    def showImage(self, calledFromButton):
        self.parent.panel.displayimg = ImageTk.PhotoImage(
            self.activeImage.resized)
        self.parent.panel.itemconfig(self.parent.panel.show,
                                     image=self.parent.panel.displayimg)
        self.parent.artist.set(self.activeImage.artist)
        if self.parent.artist.get() == "":
            self.parent.panel.itemconfig(self.parent.panel.artistWindow,
                                         state="hidden")
        else:
            self.parent.panel.itemconfig(self.parent.panel.artistWindow,
                                         state="normal")
        if self.parent.running.get() == "Running":
            self.func = self.nextImage
        if self.parent.running.get() == "Paused":
            self.func = self.passer
        self.parent.nextAlarm = self.parent.after(self.intervalTime,
                                                  self.func)


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


class root(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.childWindows = 0
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
        self.preImageList = list()
        os.chdir(self.folder)
        self.uniSource = os.getcwdu()
        for fname in os.listdir(self.uniSource):
            path = os.path.join(self.uniSource, fname)
            if os.path.isdir(path):
                continue
            if fname.endswith(('.jpg', '.png', '.jpeg', '.gif')):
                self.preImageList.append(fname)
        shuffle(self.preImageList)
        self.imageListArray = list()
        for i in xrange(0, len(self.preImageList),
                        int(len(self.preImageList) / self.numberOfMonitors)):
            self.imageListArray.append(self.preImageList[i:i + (
                int(len(self.preImageList) / self.numberOfMonitors))])

    def initDisplays(self):
        self.display = pyglet.window.get_platform().get_default_display()
        self.monitors = self.display.get_screens()
        self.startingOffset = self.interval / len(self.displaysToUse)


class slideShowWindow(tk.Toplevel):
    def __init__(self, parent, monitor, imagelist, interval, offset):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.monitor = monitor
        self.offset = offset
        self.interval = interval
        self.imageList = imageList(self, imagelist)
        self.artist = tk.StringVar()
        self.artist.set(None)
        self.running = tk.StringVar()
        self.running.set("Paused")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure(background='black')
        # make it cover the entire screen
        self.overrideredirect(1)
        if self.monitor.x < 0:
            self.geometry(
                "%dx%d+%+d%+d" % (self.monitor.width, self.monitor.height,
                                  self.monitor.x, self.monitor.y))
        else:
            self.geometry(
                "%dx%d%+d%+d" % (self.monitor.width, self.monitor.height,
                                 self.monitor.x, self.monitor.y))
        if self.monitor.x > 1000:
            # work on this logic - should sum all monitors' width to get total
            # canvas, then determine percentages of
            # canvas occupied by each screen. Can then set commandpos according
            # to margin of each. can also set update order based on this =
            # reorder monitorlist in place before iterating constructors.
            self.commandpos = 0.05
        else:
            self.commandpos = 0.95
        self.makePanel()
        self.bind('<Key-Escape>', self.closeWindow)
        self.panel.bind('<Enter>', self.showButtons)
        self.panel.bind('<Leave>', self.hideButtons)
        self.parent.childWindows += 1

    def makePanel(self):
        self.panel = tk.Canvas(self, bd=0, highlightthickness=0)
        self.panel.pack(fill="both", expand=1)
        self.panel.pw = self.monitor.width / 2
        self.panel.ph = self.monitor.height / 2
        self.panel.configure(background='black')
        self.panel.imagetoshow = None
        self.panel.show = self.panel.create_image(self.panel.pw,
                                                  self.panel.ph,
                                                  image=self.panel.imagetoshow,
                                                  anchor="center", tags="IMG")
        if self.parent.debugIndex is True:
            self.label = tk.Label(self.panel,
                                  textvariable=self.imageList.loadedIndex,
                                  font=("Calibri", "36"), background="white")
            self.panel.create_window(self.monitor.width / 2,
                                     self.monitor.height / 2,
                                     window=self.label)
        self.artistLabel = tk.Label(self.panel,
                                    textvariable=self.artist,
                                    font=("Calibri", "16"), fg="white",
                                    background="black")
        self.panel.artistWindow = self.panel.create_window(
            self.monitor.width / 2, self.monitor.height, anchor="s",
            window=self.artistLabel)
        self.nextButton = ttk.Button(self.panel, text=">",
                                     command=self.nextImage)
        self.prevButton = ttk.Button(self.panel, text="<",
                                     command=self.prevImage)
        self.pauseButton = ttk.Button(self.panel, textvariable=self.running,
                                      command=self.pauseUnpause)
        self.openButton = ttk.Button(self.panel, text="Open",
                                     command=self.openExternal)
        self.nextAlarm = self.after(self.offset,
                                    self.imageList.updateActiveImage,
                                    False)
        self.running.set("Running")

    def closeWindow(self, event):
        self.parent.totalImages.set(self.parent.totalImages.get() +
                                    self.imageList.loadedIndex.get())
        if self.parent.childWindows == 1:
            self.parent.destroy()
        else:
            self.parent.childWindows -= 1
            self.destroy()

    def showButtons(self, event):
        self.panel.create_window(int(self.monitor.width * 0.95),
                                 self.monitor.height / 2,
                                 window=self.nextButton, tags="button")
        self.panel.create_window(int(self.monitor.width * self.commandpos),
                                 int(self.monitor.height * 0.95),
                                 window=self.pauseButton, tags="button")
        self.panel.create_window(int(self.monitor.width * self.commandpos),
                                 int(self.monitor.height * 0.05),
                                 window=self.openButton, tags="button")
        self.panel.create_window(int(self.monitor.width * 0.05),
                                 self.monitor.height / 2,
                                 window=self.prevButton, tags="button")

    def hideButtons(self, event):
        self.panel.delete("button")

    def prevImage(self):
        self.after_cancel(self.nextAlarm)
        self.imageList.prevImage()

    def nextImage(self):
        self.after_cancel(self.nextAlarm)
        self.imageList.nextImage()

    def pauseUnpause(self):
        if self.running.get() == "Running":
            self.after_cancel(self.nextAlarm)
            self.running.set("Paused")
        else:
            self.running.set("Running")
            self.imageList.updateActiveImage("unpause")

    def openExternal(self):
        os.startfile(self.imageList.activeImage.ordFName)

handleExceptions()
logfilename = 'system.log'
log = logging.getLogger()
logging.basicConfig(filename=logfilename, level=logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
log.addHandler(handler)
log.info('DevilScreens started at ' + time.strftime("%c"))

root = root(None)
root.withdraw()

root.mainloop()

log.info('DevilScreens closed at ' + time.strftime("%c"))
log.info('Showed ' + str(root.totalImages.get()) + ' total images')
exit()
