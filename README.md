# DevilScreens
Idle screens are the Devil's playthings. This is a simple, configurable multimonitor slideshow that will allow you to run fullscreen slideshows of whatever you want on your idle monitors. Playback is controllable - pause/next/previous/open file.

Requirements
------------
At present, a working Python 2.7 environment, PIL, and Pyglet.

You can get Pyglet from pip install pyglet.

If you're on Windows, get PIL from here: http://www.lfd.uci.edu/~gohlke/pythonlibs/

Once you've got that, download the repo and run devilscreens.pyw.

Usage
------------
Right now the app works off an INI file, which will be generated with sensible defaults the first time you run it. I'm going to code a config GUI one of these days. The options in the INI are as follows:

- Interval: this is the interval, in seconds, between slides.
- Offset: Choose whether or not you want the refresh timers offset or not. When this is "yes", which is the default, the app will delay any monitors after the first by an amount of time such that all monitors refresh an equal amount of seconds apart from each other (so, for interval = 15 and 3 monitors, it would go update 1, wait 5, update 2, wait 5, update 3, wait 5, update 1, and so on).

If this is "no", update is synchronized across all monitors.
- Folder: This is the folder you want to display. All files ending in JPG/PNG/JPEG/GIF in this folder will be shuffled and divided into N groups, where N is the number of monitors you're using. Animated GIFs do not work (yet?)

The default is the folder that devilscreens.pyw is in. I should probably fix that but I am not sure how to do so in a platform-agnostic fashion.
- Monitors: Which monitors to display on. This should be in the form 1,2,3 et cetera. For now there is no way other than trial and error to determine which monitor is which, but I'll fix this when I add the GUI.
- Themes: A comma-separated list of the themes you want to use. There are currently four themes included; however, you can use literally any icons you like by copying my themes folder structure and naming. Template PSDs are included, feel free to go nuts with them (and send me a pull request if you do so I can include your themes!)

If you include more than one theme in the list, your first monitor will pick the first one, your second monitor will pick the second, and so on cycling through them. It will loop, so you can (for example) run 2 themes on 3 monitors or what have you (in that case, monitors 1 and 3 would use the first theme and monitor 2 would use the second).
- Index Display: This shows a big ugly number in the middle of each monitor corresponding to the internal list index of the image being shown. You should leave it turned off unless you found a bug and you're trying to figure it out, in which case let me know and thanks.

Once you've actually got a slideshow going, mouse over each window to show buttons. Buttons are next, previous, pause, play (replaces pause when paused) and share, which right now just opens the file in your default image viewer. 
- Pausing and unpausing *will* mess up the timing right now - the interval will stay the same, but the synchronization between monitors will be totally verkakte. I need to write a proper clock scheduler for this, which is high on the to do list.
- You can absolutely hit previous until you go back to before the first image in the show - you'll just start going through images from the back to the front at that point. Going forward will eventually bring you back to the start and you can continue forwards. The list of files is implemented as an infinite wraparound list (so if you run out, it starts over, forever). This does mean that if you're running multiple monitors you can never see the same picture on two different screens without restarting the app. Hmm. Maybe I'll add some config options about that.

Other Stuff
-----------
- Errors are logged to a file called system.log. If you hit any let me know by submitting an issue.

- I wrote this to work on files automatically exported by Hydrus Network (https://github.com/hydrusnetwork/hydrus). For this reason it will look for any string in the filename __surrounded by four underscores__ and will display this string in a label at the bottom of the window if found; the intent is that you could use that to show the artist/photographer/location/whatever namespace that you have tagged in Hydrus by running this against an export folder you've configured to put that namespace in the filename surrounded by four underscores.

If you're not using Hydrus, and you're the kind of person who will use this program, you should be.
