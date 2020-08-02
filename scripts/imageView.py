import os
import sys
import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(2) # this could only be used when your version of windows >= 8.1

if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    import Tkinter
    tkinter = Tkinter #I decided to use a library reference to avoid potential naming conflicts with people's programs.
else:
    import tkinter
from PIL import Image, ImageTk

# fsw =  # the fullscreen window
class State():
    def __init__(self):
        self.imageList = ['c:/tmp/test01.jpg','c:/tmp/test02.jpg','c:/tmp/test03.jpg']
        self.imageIndex = 0
        self.fullScreen = False
        self.pilImage = None
        self.image = None
        self.scaleMode = 1
        self.zoom = 1


    def nextImage(self):
        self.imageIndex = (self.imageIndex + 1)%len(self.imageList)
        self.zoom = 1
        self.loadImage()

    def previousImage(self):
        self.imageIndex = (self.imageIndex - 1)%len(self.imageList)
        self.zoom = 1
        self.loadImage()

    def loadImage(self):
        img = self.imageList[self.imageIndex]
        self.zoom = 1
        print('Showing:', img, flush=True)
        root.title(os.path.basename(img))
        self.pilImage = Image.open(img)
        showPIL(self.pilImage)
        
    def fullScreenToggle(self):
        self.fullScreen = not self.fullScreen
        showPIL(self.pilImage)
        print('Full Screen is:', self.fullScreen, flush=True)

    def setScaleMode(self, mode):
        self.scaleMode = mode
        print('Scale Mode is:', self.scaleMode, flush=True)
        showPIL(self.pilImage)

    def setZoom(self, zoom):
        self.zoom = self.zoom * zoom
        print('Zoom is:', self.zoom, flush=True)
        showPIL(self.pilImage)

state = State()
root = tkinter.Tk()

def showPIL(pilImage):
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    imgWidth, imgHeight = pilImage.size
    imgWidth = int(imgWidth*state.zoom)
    imgHeight = int(imgHeight*state.zoom)

    if state.fullScreen:
        root.overrideredirect(1) #hide the window decorations
    else:
        root.overrideredirect(0) #hide the window decorations
        w, h = (imgWidth  if imgWidth  < w else w, imgHeight if imgHeight < h else h )
    rg = "%dx%d+0+0" % ( w, h)
    print(rg, flush=True)
    root.geometry(rg)
#    w, h = (600, 400)
#    root.focus_set()    
#    root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
    frame.configure(background='black', width=w, height=h)
    if state.scaleMode == 2:
        if imgWidth > w or imgHeight > h:
            ratio = min(w/imgWidth, h/imgHeight)
            imgWidth = int(imgWidth*ratio)
            imgHeight = int(imgHeight*ratio)
    elif state.scaleMode == 3:
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
    elif state.scaleMode == 4:
        imgWidth = w
        imgHeight = h
    elif state.scaleMode == 5:
        ratio = w/imgWidth
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
    elif state.scaleMode == 6:
        ratio = h/imgHeight
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
    elif state.scaleMode == 7:
        ratio_h = h/imgHeight
        ratio_w = w/imgWidth
        if ratio_h < ratio_w:
            imgWidth = int(imgWidth*ratio_h)
            imgHeight = int(imgHeight*ratio_h)
        else:
            imgWidth = int(imgWidth*ratio_w)
            imgHeight= int(imgHeight*ratio_w)
    else:
        pass
    pilImage = pilImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)
    state.image = ImageTk.PhotoImage(pilImage)
    imagesprite = frame.create_image(w/2,h/2,image=state.image)

def key(event):
    print ("pressed", repr(event.char), flush=True)
    x = str(event.char)


def callback(event):
    print ("clicked at", event.x, event.y, flush=True)

root.tk.call('tk', 'scaling', 1.0)


frame = tkinter.Canvas(root, width=600, height=400)
frame.bind("<Key>", key)
frame.bind("<space>", lambda e: state.nextImage() )
frame.bind("<BackSpace>", lambda e: state.previousImage() )
frame.bind("1", lambda e: state.setScaleMode(1) )
frame.bind("2", lambda e: state.setScaleMode(2) )
frame.bind("3", lambda e: state.setScaleMode(3) )
frame.bind("4", lambda e: state.setScaleMode(4) )
frame.bind("5", lambda e: state.setScaleMode(5) )
frame.bind("6", lambda e: state.setScaleMode(6) )
frame.bind("7", lambda e: state.setScaleMode(7) )
frame.bind("=", lambda e: state.setZoom(1.1) )
frame.bind("+", lambda e: state.setZoom(1.1) )
frame.bind("-", lambda e: state.setZoom(0.9) )
frame.bind("<Escape>",  lambda e: (state.fullScreenToggle() if state.fullScreen else e.widget.quit()))
frame.bind("<Return>",  lambda e: (state.fullScreenToggle() ) )
frame.bind("<Button-1>",  lambda e: state.nextImage() )
frame.bind("<Button-3>",  lambda e: state.previousImage() )
frame.pack()
frame.focus_set()

state.loadImage()

root.mainloop()