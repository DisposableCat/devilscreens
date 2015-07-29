from PIL import Image

button = "pause"
template = "clearCircles"
background = "back"
stroke = "#00aa00"
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
    for y in xrange(icon.size[1]):
        for x in xrange(icon.size[0]):
            if (pix[x, y][0] - pix[x,y][1]) < 10:
                if pix[x, y][3] > 200:
                    rgbt = list(srgb)
                    if pix[x,y] > (32,32,32):
                        rgbt[0] = rgbt[0] - (255 - pix[x, y][0])
                        rgbt[1] = rgbt[1] - (255 - pix[x, y][1])
                        rgbt[2] = rgbt[2] - (255 - pix[x, y][2])
                    rgbt.append(pix[x, y][3])
                    rgbt = tuple(rgbt)
                    pix[x, y] = rgbt
            elif pix[x, y][0] > (100) and pix[x, y][1:3] < (64, 64):
                if pix[x, y][3] < 200:
                    rgbt = list(frgb)
                    rgbt[0] = rgbt[0] - (255 - pix[x, y][0])
                    #rgbt[1] = rgbt[1] - (255 - pix[x, y][1])
                    #rgbt[2] = rgbt[2] - (255 - pix[x, y][2])
                    rgbt.append(pix[x, y][3])
                    rgbt = tuple(rgbt)
                    pix[x, y] = rgbt
            else:
                print pix[x, y]
    return icon


if __name__ == '__main__':
    iconAssembler(button, template, stroke, fade, background)
