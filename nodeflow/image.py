from typing import Callable, Any, Hashable
from core import Operator, Constant, evaluate
from pathlib import Path

import PIL
from PIL import Image
from PIL.ImageEnhance import Contrast
import numpy as np

from urllib.request import urlopen
import imageio



class Texture:
    def __init__(self):
        pass


class Read(Operator):
    def __init__(self, url:Constant):
        super().__init__(url)

    def __call__(self, url:Path):
        return Image.open(urlopen(url))


class ToTexture(Operator):
    def __init__(self, image):
        super().__init__(image)

    def __call__(self, img):
        texture = Texture()
        return texture


class ToRec709(Operator):
    def __init__(self, texture:Operator):
        super().__init__(texture)

    def __call__(self, img: Image):
        colored_texture = "HELLO COLORSPACE"
        return colored_texture


if __name__ == "__main__":
    filename = Constant("https://www.andraszalavari.com/assets/media/200130_MG_1696.jpg")
    read1 = Read(filename)
    tex = ToTexture(read1)
    rec709 = ToRec709(tex)

    # cache works if call Request print only once!
    result = evaluate(read1)

    print(np.array(result))



    from tkinter import *  
    from PIL import ImageTk,Image  
    root = Tk()  
    canvas = Canvas(root, width = 300, height = 300)  
    canvas.pack()  
    img = ImageTk.PhotoImage(result.resize((300,300)))  
    canvas.create_image(20, 20, anchor=NW, image=img) 
    root.mainloop() 


