from __future__ import division
import Tkinter as tk
import ttk
import os
from random import shuffle
import ConfigParser
import re
import logging

from PIL import Image
from PIL import ImageTk
import pyglet
import collections


class imageList(object):
    def __init__(self, data):
        self.filenames = filenameList(data)

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, item):
        return self.filenames[item]


class filenameList(collections.Sequence):
    def __init__(self, data):
        self.list = list(data)

    def __len__(self):
        return len(self.list)

    def __getitem__(self, item):
        return self.list[item % len(self.list)]


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


def showImage(window, intervaltime, filename, calledFromButton):
    try:
        window.file = imageObject(filename)
    except Exception, e:
        logging.exception(e)
    w, h = window.monitor.width, window.monitor.height
    iw, ih = window.file.image.size
    ratio = min(w / iw, h / ih)
    size = int(iw * ratio), int(ih * ratio)
    resized = window.file.image.resize(size, resample=Image.BICUBIC)
    window.panel.displayimg = ImageTk.PhotoImage(resized)
    window.panel.itemconfig(window.panel.show, image=window.panel.displayimg)
    window.artist.set(window.file.artist)
    if window.artist.get() == "":
        window.panel.itemconfig(window.panel.artistWindow, state="hidden")
    else:
        window.panel.itemconfig(window.panel.artistWindow, state="normal")
    window.lastButton = calledFromButton
    if calledFromButton is "unpause":
        intervaltime = window.interval
    if calledFromButton is not "prev":
        window.showindex.set(window.showindex.get() + 1)
    # should call window.nextImage() perhaps?
    window.nextAlarm = window.after(intervaltime, showImage, window, intervaltime,
                                    window.imagelist[window.showindex.get()], False)
    return


class root(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.childWindows = 0
        (self.displaysToUse, self.numberOfMonitors, self.interval, self.folder, self.debugIndex, self.offsetCount,
         self.displaysUsed, self.displayId, self.preImageList, self.uniSource, self.imageListArray, self.display,
         self.monitors, self.startingOffset) = (None,) * 14
        self.initialize()

    def initialize(self):
        self.config = ConfigParser.ConfigParser()
        self.readConfig()
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
        for each in self.displaysToUse:
            offset = int(self.startingOffset * self.displayId)
            self.displaysUsed.append(slideShowWindow(self, self.monitors[each],
                                                     self.imageListArray[each], self.interval, offset))
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
        for i in xrange(0, len(self.preImageList), int(len(self.preImageList) / self.numberOfMonitors)):
            self.imageListArray.append(
                imageList(self.preImageList[i:i + (int(len(self.preImageList) / self.numberOfMonitors))]))

    def initDisplays(self):
        self.display = pyglet.window.get_platform().get_default_display()
        self.monitors = self.display.get_screens()
        self.displaysToUse = [0, 1]
        self.startingOffset = self.interval / len(self.displaysToUse)


class slideShowWindow(tk.Toplevel):
    def __init__(self, parent, monitor, imagelist, interval, offset):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.monitor = monitor
        self.offset = offset
        self.interval = interval
        self.imagelist = imagelist
        (self.panel, self.showindex, self.label, self.artistLabel, self.nextAlarm, self.nextButton, self.commandpos,
         self.prevButton, self.pauseButton, self.openButton,) = (None,) * 10
        self.artist = tk.StringVar()
        self.artist.set(None)
        self.running = tk.StringVar()
        self.running.set("Paused")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.initialize()
        self.parent.childWindows += 1

    def initialize(self):
        self.configure(background='black')
        # make it cover the entire screen
        self.overrideredirect(1)
        if self.monitor.x < 0:
            self.geometry("%dx%d+%+d%+d" % (self.monitor.width, self.monitor.height,
                                            self.monitor.x, self.monitor.y))
        else:
            self.geometry("%dx%d%+d%+d" % (self.monitor.width, self.monitor.height,
                                           self.monitor.x, self.monitor.y))
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
        self.showindex = tk.IntVar()
        self.showindex.set(0)
        if self.parent.debugIndex is True:
            self.label = tk.Label(self.panel,
                                  textvariable=self.showindex, font=("Calibri", "36"), background="white")
            self.panel.create_window(self.monitor.width / 2, self.monitor.height / 2, window=self.label)
        self.artistLabel = tk.Label(self.panel,
                                    textvariable=self.artist, font=("Calibri", "16"), fg="white", background="black")
        self.panel.artistWindow = self.panel.create_window(self.monitor.width / 2, self.monitor.height, anchor="s",
                                                           window=self.artistLabel)
        self.bind('<Key-Escape>', self.closeWindow)
        self.nextButton = ttk.Button(self.panel, text=">", command=self.nextImage)
        if self.monitor.x > 1000:
            # work on this logic - should sum all monitors' width to get total canvas, then determine percentages of
            # canvas occupied by each screen. Can then set commandpos according to margin of each.
            # can also set update order based on this = reorder monitorlist in place before iterating constructors.
            self.commandpos = 0.05
        else:
            self.commandpos = 0.95
        self.panel.create_window(int(self.monitor.width * 0.95), self.monitor.height / 2, window=self.nextButton)
        self.prevButton = ttk.Button(self.panel, text="<", command=self.prevImage)
        self.panel.create_window(int(self.monitor.width * 0.05), self.monitor.height / 2, window=self.prevButton)
        self.pauseButton = ttk.Button(self.panel, textvariable=self.running, command=self.pauseUnpause)
        self.panel.create_window(int(self.monitor.width * self.commandpos), int(self.monitor.height * 0.95),
                                 window=self.pauseButton)
        self.openButton = ttk.Button(self.panel, text="Open", command=self.openExternal)
        self.panel.create_window(int(self.monitor.width * self.commandpos), int(self.monitor.height * 0.05),
                                 window=self.openButton)
        self.nextAlarm = self.after(self.offset, showImage, self, self.interval, self.imagelist[self.showindex.get()],
                                    False)
        self.running.set("Running")

    def closeWindow(self, event):
        if self.parent.childWindows == 1:
            self.parent.destroy()
        else:
            self.parent.childWindows -= 1
            self.destroy()

    def prevImage(self):
        self.showindex.set(self.showindex.get() - 1)
        self.after_cancel(self.nextAlarm)
        self.nextAlarm = self.after(0, showImage, self, self.interval, self.imagelist[self.showindex.get() - 1], "prev")

    def nextImage(self):
        self.after_cancel(self.nextAlarm)
        self.nextAlarm = self.after(0, showImage, self, self.interval, self.imagelist[self.showindex.get()], "next")

    def pauseUnpause(self):
        # possibly buggy in re next/prev while paused
        if self.running.get() == "Running":
            self.after_cancel(self.nextAlarm)
            self.running.set("Paused")
        else:
            self.nextAlarm = self.after(0, showImage, self, 0, self.imagelist[self.showindex.get()], "unpause")
            self.running.set("Running")

    def openExternal(self):
        os.startfile(self.imagelist[self.showindex.get() - 1])


logfilename = 'error.log'
logging.basicConfig(filename=logfilename, level=logging.DEBUG)

root = root(None)
root.withdraw()

root.mainloop()

print 'closing'
exit()
