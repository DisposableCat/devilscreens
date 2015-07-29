from PIL import Image

def iconAssembler(button,  template, background):
    buttonFilename = "\\themes\\" + template + "\\" + button + ".png"
    back = Image.open("\\themes\\" + background)
    icon = Image.open(buttonFilename)
    final = Image.composite(back, icon)
    final.show()

