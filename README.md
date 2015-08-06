
# DevilScreens
Idle screens are the Devil's playthings. This is a simple, configurable multimonitor slideshow that will allow you to run fullscreen slideshows of whatever you want on your idle monitors. Playback is controllable - pause/next/previous/open 
file. Buttons auto-hide when you're not moused over the screen they're on.

Requirements
------------
At present:
- a working Python 2.7 environment
- Pillow
- Pyglet 1.2+
- this should be platform-agnostic (for anything with Pyglet anyway) but I 
haven't tested
 on anything but 
Windows. If you experience difficulty with some other OS let me know and 
we'll troubleshoot so that I can fix it.


You can get Pyglet from pip install pyglet.

If you're on Windows, get Pillow from here: http://www.lfd.uci
.edu/~gohlke/pythonlibs/

Once you've got all that, download the repo and run devilscreens.pyw.

Screenshot
-----------
[main view](/docs/screenshot.png?raw=true)

Usage
------------

The app has a rudimentary configuration GUI, which is a work in progress. 
This window will be displayed upon startup. Options available via the GUI 
are as follows:

- Folder: This is the folder DevilScreens is currently set to display. All 
files ending in JPG/PNG/JPEG/GIF in this folder will be shuffled and divided into N groups, where N is the number of monitors you're using. Animated GIFs do not work (yet?) The "..." button brings up the folder picker.
 - The default is the folder that devilscreens.pyw is in. I should probably fix that but I am not sure how to do so in a platform-agnostic fashion.
- Image cycle time: this is the interval, in seconds, between slides.
- Offset timers?: Choose whether or not you want the refresh timers offset or not. When this is "yes", which is the default, the app will delay any monitors after the first by an amount of time such that all monitors refresh an equal amount of seconds apart from each other (so, for interval = 15 and 3 monitors, it would go update 1, wait 5, update 2, wait 5, update 3, wait 5, update 1, and so on).
 - If this is "no", update is synchronized across all monitors.
- Monitors: All detected monitors are shown with their resolution, displayed
 in order of X coordinate on the overall system canvas (so, they should 
 appear in the GUI in the same order they appear in physical space). Each 
 monitor has a checkbox which indicates whether or not DevilScreens will use
  it.
- Start Show: Self-explanatory; this starts the show.
- Quit: Also self-explanatory.
  
There are several other options available via slideshow.ini, which also 
saves the options you set in the GUI. Eventually these will all appear in 
the GUI as well. The additional options in the INI are currently as follows:

- Background color: The color to use for the background of the image windows
 and text labels.
- Text color: The color to use for label text. Should not be the same as above.
- Themes: A comma-separated list of the themes you want to use. There are 
currently two themes included. Themes represent button shapes and the 
appropriate Photoshop layer effects to make them look good. They are 
combined with colors and backgrounds to generate button graphics on the fly 
in a highly customizable way.
- Colors: The colors to use for your chosen themes, in ```#rrggbb``` hex code 
format. There should be the same number of colors as the number of 
non-background/mask layers in your chosen themes, separated by ```/```. 
Multiple colorsets can be comma-separated. ```/same/``` as a color choice will 
cause the original color of the corresponding layer to be used.
- Backgrounds: The background images to use for your themes. These should be
 128x128 pixel PNGs, which can include transparency, and should be in 
 ```/themes/backgrounds```. Do not include the extension in the INI entry.
 - If you include more than one theme/color/background in the list, your first monitor will pick the first one, your second monitor will pick the second, and so on cycling through them. It will loop, so you can (for example) run 2 themes on 3 monitors or what have you (in that case, monitors 1 and 3 would use the first theme and monitor 2 would use the second). This is independent - you could 
 pick 3 themes, 2 colorsets, and 1 background, or the reverse, or whatever, 
 and everything would work fine. (Individual colorsets do NOT loop, though. 
 So you can't specify 1 color for a 3 color theme and expect it to work.)
- Index Display: This shows a big ugly number in the middle of each monitor corresponding to the internal list index of the image being shown. You should leave it turned off unless you found a bug and you're trying to figure it out, in which case let me know and thanks.

Once you've actually got a slideshow going, mouse over each window to show buttons. Buttons are next, previous, pause, play (replaces pause when paused) and share, which right now just opens the file in your default image viewer. 
- Pausing and unpausing *will* mess up the timing right now - the interval will stay the same, but the synchronization between monitors will be totally verkakte. I need to write a proper clock scheduler for this, which is high on the to do list.
- You can absolutely hit previous until you go back to before the first image in the show - you'll just start going through images from the back to the front at that point. Going forward will eventually bring you back to the start and you can continue forwards. The list of files is implemented as an infinite wraparound list (so if you run out, it starts over, forever). This does mean that if you're running multiple monitors you can never see the same picture on two different screens without restarting the app. Hmm. Maybe I'll add some config options about that.

Theme Format
-----------
- Themes are stored as subfolders in ```themes```. Each folder contains, for
 each of the 5 buttons used by the program (next/prev/pause/share/play):
 - A mask to be applied to the background ```playMask.png```
 - One or more semitransparent layers, in the format ```play0.png, play1.png,..
 .```  continuing to increment as necessary.
 - A Photoshop template containing the source layers for all of this, which 
 is optional and not used by the program itself. ```template.psd```
 - Technically speaking, layers can be any color (but should be a uniform 
 color). The color engine simply replaces whatever color is used in the 
 layer with the color specified in the INI at the same alpha. If you want to
  use sensible default values, go ahead - I use bright neon green and pink 
  because of how I hoped to implement this feature (which didn't work out). 
  I suggest using ```0xffffff/same/0x000000``` with my themes for most backgrounds, 
  but play with it.
 - I've included, under Docs, a modified version of Photoshop CS6's "Export 
 Layers to Files.jsx" script, which exports layers to files with the 
 filenames set to be exactly what the layer names are. This streamlines 
 saving all the individual bits of a theme.

Other Stuff
-----------
- Errors are logged to a file called system.log. If you hit any let me know by submitting an issue.

- I wrote this to work on files automatically exported by Hydrus Network (https://github.com/hydrusnetwork/hydrus). For this reason it will look for any string in the filename ```__surrounded by four underscores__``` and will display this string in a label at the bottom of the window if found; the intent is that you could use that to show the artist/photographer/location/whatever namespace that you have tagged in Hydrus by running this against an export folder you've configured to put that namespace in the filename surrounded by four underscores.

If you're not using Hydrus, and you're the kind of person who will use this program, you should be.
