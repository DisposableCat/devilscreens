#!/usr/bin/env python
"""devilscreens.pyw: a configurable multimonitor slideshow"""
from __future__ import division
import Tkinter as tk
import tkFileDialog
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
import operator

from PIL import Image
from PIL import ImageTk
import pyglet
from iconsassemble import iconAssembler


# Copyright (c) 2015 Peter K Cawley. Released under MIT license; see
# LICENSE.txt

def handleExceptions():
    # with thanks to Brad Barrows:
    # http://stackoverflow.com/questions/1508467/
    old_print_exception = traceback.print_exception

    def custom_print_exception(etype, value, tb, limit=None, files=None):
        tb_output = traceback.format_exception(etype, value, tb)
        tb_output = list("\n") + tb_output
        fullException = "\n".join(tb_output)
        log.error(fullException)
        log.info('DevilScreens crashed at ' + time.strftime("%c"))
        sys.exit(1)

    traceback.print_exception = custom_print_exception


handleExceptions()
logfilename = 'system.log'
log = logging.getLogger()
logging.basicConfig(filename=logfilename, level=logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
log.addHandler(handler)
log.info('DevilScreens started at ' + time.strftime("%c"))


def silenceErr():
    def write(self, s):
        pass


class usableScreen:
    def __init__(self, Screen):
        lmargin, rmargin, tmargin, bmargin = 0.06, 0.94, 0.06, 0.90
        self.x = Screen.x
        self.y = Screen.y
        self.w = Screen.width
        self.h = Screen.height
        if self.x < 0:
            self.setPos(rmargin, '+')
        if self.x > 0:
            self.setPos(lmargin, '')
        if self.x == 0:
            self.setPos(0.5, '')
        self.dimensions = (self.w, self.h, self.gSign, self.x, self.y,)
        self.pw = self.w / 2
        self.ph = self.h / 2
        self.t = int(self.h * tmargin)
        self.b = int(self.h * bmargin)
        self.l = int(self.w * lmargin)
        self.r = int(self.w * rmargin)

    def setPos(self, percent, string):
        self.cPos = int(self.w * percent)
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


class fancyButton:
    def __init__(self, parent, button, function):
        self.parent = parent
        self.button = button
        self.function = function
        self.toggleFunc = None
        if self.button == "pause":
            self.toggleFunc = "play"
        self.buttons = {"share": "ct", "next": "rh", "prev": "lh",
                        "pause": "cb",
                        "play": "cb"}
        self.icon = self.makeIcon(self.button)
        self.parent.p.tag_bind(self.button, "<ButtonPress-1>", self.onClick)

    def makeIcon(self, button):
        status, newImg = iconAssembler(self.parent.baseDir, button,
                                       self.parent.theme,
                                       self.parent.colors,
                                       self.parent.background)
        if newImg is None:
            log.error(status)
            # try again with default values
            status, newImg = iconAssembler(self.parent.baseDir, button,
                                           "circled", "0xffffff,same,0x000000",
                                           "silver")
        newImg = ImageTk.PhotoImage(newImg)
        return newImg

    def createButton(self):
        m = self.parent.m
        coords = {"t": m.t, "b": m.b, "c": m.cPos, "h": m.ph, "l": m.l,
                  "r": m.r}
        (x, y) = self.buttons.get(self.button)
        (x, y) = coords.get(x), coords.get(y)
        self.parent.p.create_image(x, y, image=self.icon, anchor="center",
                                   tags=(self.button, "button"))

    def onClick(self, event):
        if self.toggleFunc is not None:
            self.parent.p.delete(self.button)
            self.toggleFunc, self.button = self.button, self.toggleFunc
            self.icon = self.makeIcon(self.button)
            self.createButton()
            self.parent.p.tag_bind(self.button, "<ButtonPress-1>",
                                   self.onClick)
        self.function()

    def isToggler(self, secondbutton):
        self.altIcon = self.makeIcon(secondbutton)


class monitorFrame:
    def __init__(self, parent, count, monitor):
        self.parent = parent
        self.monitorFrame = tk.Frame(self.parent)
        self.toggleVar = tk.StringVar()
        self.monitor = monitor
        self.monitorFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.toggleButton = ttk.Checkbutton(self.monitorFrame,
                                            text="Monitor " + str(count + 1),
                                            variable=self.toggleVar,
                                            onvalue=str(count + 1),
                                            offvalue='')
        self.label = ttk.Label(self.monitorFrame, text="{0}x{1}".format(
            str(self.monitor.w), str(self.monitor.h)), justify=tk.CENTER)
        self.toggleButton.pack()
        self.label.pack()


class configFrame:
    def __init__(self, parent):
        self.parent = parent
        self.rootFrame = tk.Frame()
        self.rootFrame.pack(fill=tk.X, expand=1)
        self.makeTopFrame()
        self.makeIntervalFrame()
        self.makeMonitorFrame()
        self.makeBottomFrame()

    def makeTopFrame(self):
        self.topFrame = tk.Frame(self.rootFrame)
        self.topFrame.pack()
        title = ttk.Label(self.topFrame, text="DevilScreens Config")
        title.pack()
        self.folderVar = tk.StringVar()
        self.folderVar.set(self.parent.folder)
        folderLabel = ttk.Label(self.topFrame, text="Folder:")
        folderLabel.pack(side=tk.LEFT, padx=2)
        folder = ttk.Label(self.topFrame, textvariable=self.folderVar)
        folder.pack(side=tk.LEFT)
        browseButton = ttk.Button(self.topFrame, command=self.selectFolder,
                                  text='...', width=3)
        browseButton.pack(padx=2)

    def selectFolder(self):
        folder = tkFileDialog.askdirectory(initialdir=self.folderVar.get(),
                                           mustexist=True,
                                           parent=root)
        if folder:
            self.folderVar.set(folder)

    def makeIntervalFrame(self):
        self.intervalFrame = tk.Frame(self.rootFrame)
        self.intervalFrame.pack()
        self.makeIntervalEntry(self.intervalFrame)
        self.makeOffsetToggle(self.intervalFrame)

    def makeIntervalEntry(self, frame):
        self.vinterval = tk.StringVar()
        self.vinterval.set(str(self.parent.interval // 1000))
        self.validateInt = frame.register(self.vint)
        intervalLabel = ttk.Label(frame, text="Image cycle time (s):")
        intervalLabel.pack(side=tk.LEFT, fill=tk.X, expand=1, padx=5)
        intervalButton = ttk.Entry(frame, validate='all',
                                   validatecommand=(self.validateInt, '%P',
                                                    '%s'),
                                   textvariable=self.vinterval,
                                   justify=tk.CENTER, width=5)
        intervalButton.pack(side=tk.LEFT)

    def makeOffsetToggle(self, frame):
        self.offsetBool = tk.BooleanVar()
        self.offsetBool.set(self.parent.offsetPref)
        self.offsetToggle = ttk.Checkbutton(frame, text="Offset timers?",
                                            variable=self.offsetBool,
                                            onvalue=True, offvalue=False)
        self.offsetToggle.pack(padx=5)

    def makeMonitorFrame(self):
        self.mlistFrame = tk.Frame(self.rootFrame)
        self.monitorButtons = list()
        self.monitorVars = list()
        self.mlistFrame.pack(side=tk.TOP, fill=tk.BOTH)
        for count, monitor in enumerate(self.parent.monitors):
            self.monitorButtons.append(monitorFrame(self.mlistFrame, count,
                                                    monitor))
        for count, frame in enumerate(self.monitorButtons):
            self.monitorVars.append(frame.toggleVar)
            if count in self.parent.displaysToUse:
                frame.toggleButton.invoke()

    def makeBottomFrame(self):
        self.bottomFrame = tk.Frame(self.rootFrame)
        self.bottomFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.makeStartQuit(self.bottomFrame)

    def makeStartQuit(self, frame):
        startButton = ttk.Button(
            frame, text="Start Show", command=self.parent.startShow)
        startButton.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        quitButton = ttk.Button(
            frame, text="Quit", command=self.parent.destroy)
        quitButton.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

    def vint(self, what, prev):
        if not what:
            return True
        truth = what.isdigit()
        if truth is False:
            self.prevInterval = prev
            return False
        if truth is True:
            return True


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
        self.configGui()
        # self.startShow()

    def readConfig(self):
        if os.path.exists(os.path.join(self.baseDir, "slideshow.ini")):
            self.config.read(os.path.join(self.baseDir, "slideshow.ini"))
            self.displaysToUse = self.config.get('Config', 'monitors')
            self.displaysToUse = self.displaysToUse.split(',')
            self.displaysToUse = map(int, self.displaysToUse)
            self.displaysToUse[:] = [x - 1 for x in self.displaysToUse]
            self.numberOfMonitors = len(self.displaysToUse)
            self.interval = self.config.getint('Config', 'interval') * 1000
            self.folder = self.config.get('Config', 'folder')
            self.offsetPref = self.config.getboolean('Config', 'offset')
            self.bgColor = self.config.get('Config', 'background color')
            self.fgColor = self.config.get('Config', 'text color')
            themes = self.config.get("Theme", "themes")
            themes = themes.split(',')
            self.themes = wrappingList(themes)
            backgrounds = self.config.get("Theme", "backgrounds")
            backgrounds = backgrounds.split(',')
            self.backgrounds = wrappingList(backgrounds)
            colors = self.config.get("Theme", "colors")
            colors = colors.split(',')
            tcolors = list()
            for each in colors:
                tcolors.append(each.split('/'))
            self.colors = wrappingList(tcolors)
            self.debugIndex = self.config.getboolean('Debug', 'index display')
        else:
            self.writeConfig()
            self.readConfig()

    def writeConfig(self):
        # sensible defaults
        self.config.add_section('Config')
        self.config.set('Config', 'interval', '10')
        self.config.set('Config', 'offset', 'yes')
        self.config.set('Config', 'folder', os.getcwdu())
        self.config.set('Config', 'background color', 'black')
        self.config.set('Config', 'text color', "white")
        self.config.set('Config', 'monitors', "1")
        self.config.add_section("Theme")
        self.config.set("Theme", "themes", "circled")
        self.config.set("Theme", "backgrounds", "silver")
        self.config.set("Theme", "colors", "0xffffff,same,0x000000")
        self.config.add_section('Debug')
        self.config.set('Debug', 'index display', 'no')
        with open(os.path.join(self.baseDir, 'slideshow.ini'), 'wb') as \
                configfile:
            self.config.write(configfile)

    def saveConfig(self):
        monstring = ''
        for each in self.confGUI.monitorVars:
            if each.get() is not '':
                monstring = monstring + each.get() + ','
        monstring = monstring[:-1]
        if monstring == '':
            monstring = '1'
        self.config.set("Config", "monitors", monstring)
        self.config.set("Config", "interval", self.confGUI.vinterval.get())
        self.config.set("Config", "offset", self.confGUI.offsetBool.get())
        self.config.set("Config", "folder", self.confGUI.folderVar.get())
        with open(os.path.join(self.baseDir, 'slideshow.ini'), 'wb') as \
                configfile:
            self.config.write(configfile)

    def startShow(self):
        self.saveConfig()
        self.readConfig()
        self.setOffset()
        self.setupShuffledList()
        self.offsetCount = 0
        self.displaysUsed = list()
        self.displayId = 0
        for count, each in enumerate(self.displaysToUse):
            offset = int(self.startingOffset * self.displayId)
            self.displaysUsed.append(slideShowWindow(self, self.monitors[
                each], self.imageListArray[count], self.interval, offset,
                                                     self.themes[count],
                                                     self.colors[count],
                                                     self.backgrounds[count]))
            self.displayId += 1
        self.withdraw()

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
        if len(pImgList) == 0:
            log.error("There are no images in the source folder! Exiting")
            exit()
        shuffle(pImgList)
        self.imageListArray = list()
        for i in xrange(0, len(pImgList),
                        int(len(pImgList) / self.numberOfMonitors)):
            self.imageListArray.append(pImgList[i:i + (
                int(len(pImgList) / self.numberOfMonitors))])

    def initDisplays(self):
        self.display = pyglet.canvas.get_display()
        monlist = self.display.get_screens()
        self.monitors = list()
        for each in monlist:
            self.monitors.append(usableScreen(each))
        self.monitors.sort(key=operator.attrgetter('x', 'y'))

    def setOffset(self):
        self.startingOffset = self.interval / len(self.displaysToUse)
        if self.offsetPref is False:
            self.startingOffset = 0

    def configGui(self):
        self.confGUI = configFrame(self)


class slideShowWindow(tk.Toplevel):
    def __init__(self, parent, monitor, imagelist, interval, offset, theme,
                 colors, background):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.baseDir = parent.baseDir
        self.m = monitor
        self.offset = offset
        self.interval = interval
        self.theme = theme
        self.colors = colors
        self.background = background
        self.il = imageList(self, imagelist)
        self.artist = tk.StringVar()
        self.artist.set(None)
        self.running = tk.BooleanVar()
        self.running.set(False)
        self.configure(background='black')
        self.overrideredirect(1)
        self.geometry("%dx%d%s%+d%+d" % self.m.dimensions)
        self.makePanel()
        self.bind('<Key-Escape>', self.closeWindow)
        self.initButtons()
        self.p.bind('<Enter>', self.showButtons)
        self.p.bind('<Leave>', self.hideButtons)
        self.parent.childWindows += 1

    def makePanel(self):
        self.p = tk.Canvas(self, bd=0, highlightthickness=0)
        self.p.pack(fill="both", expand=1)
        self.p.configure(background=self.parent.bgColor)
        self.p.imagetoshow = None
        self.p.show = self.p.create_image(self.m.pw, self.m.ph,
                                          image=self.p.imagetoshow,
                                          anchor="center", tags="IMG")
        if self.parent.debugIndex is True:
            self.label = tk.Label(self.p, textvariable=self.il.loadedIndex,
                                  font=("Calibri", "36"),
                                  bg=self.parent.bgColor,
                                  fg=self.parent.fgColor)
            self.p.create_window(self.m.pw, self.m.ph, window=self.label)
        self.artistLabel = tk.Label(self.p, textvariable=self.artist,
                                    font=("Calibri", "16"),
                                    fg=self.parent.fgColor,
                                    background=self.parent.bgColor)
        self.p.artistWindow = self.p.create_window(self.m.pw, self.m.h,
                                                   anchor="s",
                                                   window=self.artistLabel)
        self.nextAlarm = self.after(self.offset, self.il.updateActiveImage,
                                    False)
        self.running.set(True)

    def closeWindow(self, event):
        # total is buggy as fuck, need to fix
        self.parent.totalImages.set(self.parent.totalImages.get() +
                                    self.il.loadedIndex.get())
        if self.parent.childWindows == 1:
            self.parent.destroy()
        else:
            self.parent.childWindows -= 1
            self.destroy()

    def initButtons(self):
        self.buttons = dict()
        buttonNames = {"next": self.nextImage, "prev": self.prevImage,
                       "share": self.shareImage, "pause": self.pauseUnpause}
        for name in buttonNames.keys():
            self.buttons[name] = (fancyButton(self, name, buttonNames.get(
                name)))

    def showButtons(self, event):
        for button in self.buttons.itervalues():
            button.createButton()

    def hideButtons(self, event):
        self.p.delete("button")

    def prevImage(self):
        self.after_cancel(self.nextAlarm)
        self.il.prevImage()

    def nextImage(self):
        self.after_cancel(self.nextAlarm)
        self.il.nextImage()

    def pauseUnpause(self):
        if self.running.get():
            self.after_cancel(self.nextAlarm)
            self.running.set(False)
            # restart delay needs fixed
        else:
            self.running.set(True)
            self.il.updateActiveImage("unpause")

    def shareImage(self):
        os.startfile(self.il.actImg.ordFName)


root = ssRoot(None)
# root.withdraw()

root.mainloop()

log.info('DevilScreens closed at ' + time.strftime("%c"))
log.info('Showed ' + str(root.totalImages.get()) + ' total images')
exit()
