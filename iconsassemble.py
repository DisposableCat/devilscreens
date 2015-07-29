from PIL import Image

button = "pause"
template = "clearCircles"
background = "back"
color = "#000080"

def iconAssembler(button, template, color, background):
    back = Image.open("themes\\backgrounds\\" + background + ".png")
    back = back.convert('RGBA')
    icon = Image.open("themes\\" + template + "\\" + button + ".png")
    icon = icon.convert('RGBA')
    icon = replaceStroke(icon, color)
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
    return (int(hexstr,16))

def replaceStroke(icon, color):
    rgb = list((cvHex(color[1:3]), cvHex(color[3:5]), cvHex(color[5:7])))
    print rgb
    pix = icon.load()
    for y in xrange(icon.size[1]):
        for x in xrange(icon.size[0]):
            if pix[x,y][0:3] == (0,0,0):
                if pix[x,y][3] > 64:
                    rgbt = list(rgb)
                    rgbt.append(pix[x,y][3])
                    rgbt = tuple(rgbt)
                    pix[x,y] = rgbt
            else:
                print pix[x,y]
    return icon

if __name__ == '__main__':
    iconAssembler(button, template, color, background)