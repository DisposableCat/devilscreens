from __future__ import division
from PIL import Image

button = "pause"
template = "clearCircles"
background = "back"
colors = ("#ba5e45", "same", "#079ad8")


def iconAssembler(button, template, colors, background):
    back = Image.open("themes\\backgrounds\\" + background + ".png")
    back = back.convert('RGBA')
    mask = Image.open("themes\\" + template + "\\" + button + "Mask.png")
    mask = mask.convert('L')
    back.putalpha(mask)
    layers = list()
    for count, color in enumerate(colors):
        filename = ''
        try:
            filename = "themes\\" + template + "\\" + button + str(
                count) + ".png"
            layer = Image.open(filename)
        except:
            status = "Not enough colors! Can't open " + filename
            return status, None
        layer = layer.convert('RGBA')
        if color != "same":
            try:
                layer = replaceColors(layer, color)
            except:
                status = "Couldn't colorshift " + filename + " to " + color \
                         + "! Possible bad color string?"
                return status, None
        back = Image.alpha_composite(back, layer)
    status = "Successfully generated icons!"
    return status, back


def cvHex(hexstr):
    return int(hexstr, 16)


def iCanTellBySomeOfThePixels(icon, pic1, pic2, pic3):
    for y in xrange(icon.size[0]):
        for x in xrange(icon.size[1]):
            currentPixel = pic1[x,y]
            comparePixel = pic2[x,y]
            if currentPixel == comparePixel:
                continue
            if currentPixel[0] == 0:
                continue
            elif currentPixel[3] is not 0:
                print str(currentPixel[0:3]) + " should be " + str(
                    comparePixel[0:3]) + " from " + str(pic3[x, y][0:3])


def replaceColors(icon, color):
    rgb = list((cvHex(color[1:3]), cvHex(color[3:5]), cvHex(color[5:7])))
    pix = icon.load()
    for y in xrange(icon.size[1]):
        for x in xrange(icon.size[0]):
            r, g, b = rgb[0:3]
            pa = pix[x, y][3]
            rgbt = (r, g, b, pa)
            pix[x, y] = rgbt
    return icon


if __name__ == '__main__':
    _, stuff = iconAssembler(button, template, colors, background)
    stuff.save("0.png")
