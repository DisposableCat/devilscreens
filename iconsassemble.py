from PIL import Image

button = "pause"
template = "clearCircles"
background = "back"
color = "#000000"

def iconAssembler(button, template, color, background):
    back = Image.open("themes\\backgrounds\\" + background + ".png")
    back = back.convert('RGBA')
    icon = Image.open("themes\\" + template + "\\" + button + ".png")
    icon = icon.convert('RGBA')
    replaceStroke(icon, color)
    mask = Image.open("themes\\" + template + "\\" + button + "Mask.png")
    mask = mask.convert('L')
#    mask.show()
    back.putalpha(mask)
#    back.show()
    final = Image.alpha_composite(back, icon)
    final.save("themes\\backgrounds\\test.png")

def replaceStroke(icon, color):
    for y in xrange(icon.size[0])

iconAssembler(button, template, color, background)