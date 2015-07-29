from PIL import Image

button = "pause"
template = "clearCircles"
background = "back"
color = "#ff00ff"

def iconAssembler(button, template, color, background):
    back = Image.open("themes\\backgrounds\\" + background + ".png")
    back = back.convert('RGBA')
    icon = Image.open("themes\\" + template + "\\" + button + ".png")
    icon = icon.convert('RGBA')
    replaceStroke(icon, color)
    #icon.show()
    mask = Image.open("themes\\" + template + "\\" + button + "Mask.png")
    mask = mask.convert('L')
#    mask.show()
    back.putalpha(mask)
#    back.show()
    final = Image.alpha_composite(back, icon)
    status = "Successfully generated icons!"
    final.save("themes\\backgrounds\\test.png")
    return status

def replaceStroke(icon, color):
    rgb = list((int(color[1:2], 16), int(color[3:4], 16), int(color[5:6],
                                                                16)))
    for y in xrange(icon.size[1]):
        for x in xrange(icon.size[0]):
            pix = icon.load()
            if pix[x,y][0:2] == (0,0,0):
                pix[x,y][0:2] = rgb

if __name__ == '__main__':
    iconAssembler(button, template, color, background)