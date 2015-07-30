from PIL import Image

button = "pause"
template = "clearCircles"
background = "back"
stroke = "#aa0000"
fade = "#000080"


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


def replaceColors(icon, stroke, fade):
    srgb = list((cvHex(stroke[1:3]), cvHex(stroke[3:5]), cvHex(stroke[5:7])))
    frgb = list((cvHex(fade[1:3]), cvHex(fade[3:5]), cvHex(fade[5:7])))
    print srgb
    pix = icon.load()

    def replaceColor(rgb, pix):
        rgbt = list(rgb)
        rgbt.append(pix[x, y][3])
        rgbt = tuple(rgbt)
        pix[x, y] = rgbt
        return pix

    for y in xrange(icon.size[1]):
        for x in xrange(icon.size[0]):
            currentPixel = pix[x, y]
            if currentPixel[0:3] in ((0,0,0),(255,255,255)):
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
                pix = replaceColor(frgb,pix)
                continue
            # elif currentPixel[0] == currentPixel[2]:
            #     pix = replaceColor(srgb,pix)
            #     continue
            # if pix[x, y][1] == 255:
            #     pix = replaceStroke(srgb,pix)
    return icon


if __name__ == '__main__':
    iconAssembler(button, template, stroke, fade, background)
