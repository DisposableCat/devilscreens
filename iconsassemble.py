from __future__ import division
from PIL import Image

button = "pause"
template = "clearCircles"
background = "back"
stroke = "#aa0000"
fade = "#000080"

def redistribute_rgb(r, g, b):
    #with thanks to Mark Ransom:
    #http://stackoverflow.com/questions/141855/
    threshold = 255.999
    m = max(r, g, b)
    if m <= threshold:
        return int(r), int(g), int(b)
    total = r + g + b
    if total >= 3 * threshold:
        return int(threshold), int(threshold), int(threshold)
    x = (3 * threshold - total) / (3 * m - total)
    gray = threshold - x * m
    return int(gray + x * r), int(gray + x * g), int(gray + x * b)


def iconAssembler(button, template, stroke, fade, background):
    back = Image.open("themes\\backgrounds\\" + background + ".png")
    back = back.convert('RGBA')
    icon = Image.open("themes\\" + template + "\\" + button + ".png")
    icon = icon.convert('RGBA')
    icon = replaceColors(icon, stroke, fade)
    icon.save("themes\\backgrounds\icon.png")
    #    icon.show()
    mask = Image.open("themes\\" + template + "\\" + button + "Mask.png")
    mask = mask.convert('L')
    #    mask.show()
    back.putalpha(mask)
    #    back.show()
    final = Image.alpha_composite(back, icon)
    status = "Successfully generated icons!"
    final.save("themes\\backgrounds\\test.png")
    return status


def cvHex(hexstr):
    return (int(hexstr, 16))

def iCanTellBySomeOfThePixels(icon, pic1, pic2):
    for y in xrange(icon.size[0]):
        for x in xrange(icon.size[1]):
            currentPixel = pic1[x,y]
            comparePixel = pic2[x,y]
            if currentPixel is not comparePixel:
                if currentPixel[3] is not 0:
                    print str(currentPixel) + " should be " + str(comparePixel)

def replaceColors(icon, stroke, fade):
    srgb = list((cvHex(stroke[1:3]), cvHex(stroke[3:5]), cvHex(stroke[5:7])))
    frgb = list((cvHex(fade[1:3]), cvHex(fade[3:5]), cvHex(fade[5:7])))
    print srgb
    pix = icon.load()
    compare = Image.open("themes\\clearCircles\\test.png")
    cpix = compare.load()

    def replaceColor(rgb, pix):
        r, g, b = rgb[0:3]
        pr, pg, pb, pa = pix[x, y][0:]
        if pr > 0:
            lightShade = pr + pg + pb
            multiplier = lightShade/255
            r, b, g = redistribute_rgb(r*multiplier,g*multiplier,
                                         b*multiplier)
        rgbt = (r, b, g, pa)
        pix[x, y] = rgbt
        return pix

    for y in xrange(icon.size[1]):
        for x in xrange(icon.size[0]):
            currentPixel = pix[x, y]
            if currentPixel[0:3] in ((0, 0, 0), (255, 255, 255)):
                continue
            elif currentPixel[3] == 999:
                continue
            elif min(currentPixel[0:3]) > 250:
                continue
            elif max(currentPixel[0:3]) == currentPixel[1]:
                if currentPixel[1] > 64:
                    pix = replaceColor(srgb, pix)
                    continue
            elif max(currentPixel[0:3]) == currentPixel[0]:
                pix = replaceColor(frgb, pix)
                continue
    iCanTellBySomeOfThePixels(icon, pix, cpix)
    return icon


if __name__ == '__main__':
    iconAssembler(button, template, stroke, fade, background)
