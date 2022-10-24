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
    import sys
    from gui import VideoPlayer
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QImage, QPixmap
    from PySide2.QtWidgets import QApplication, QWidget
    from PySide2.QtWidgets import QSlider, QLabel, QVBoxLayout
    from PIL import Image
    import re

    import pythonflow as pf

    the_cache = dict()
    def save_cache(key, obj):
        print("save cache")
        the_cache[key] = obj

    def load_cache(key):

        print("load cache", key in the_cache)
        return the_cache[key]

    # Create Graph
    with pf.Graph() as graph:
        imageio = pf.import_('imageio')
        ndimage = pf.import_('scipy.ndimage')
        np = pf.import_('numpy')
        filename = pf.placeholder('filename')
        image = (imageio.imread(filename).set_name('imread')[..., :3] / 255.0)
        cached = pf.cache(image, load_cache, save_cache, key=filename)
        cached.set_name("out")

    result = graph('out', filename="C:/Users/and/Desktop/SMPTE_colorbars/SMPTE_colorbars_00001.jpg")
    result = graph('out', filename="C:/Users/and/Desktop/SMPTE_colorbars/SMPTE_colorbars_00001.jpg")
    #print(result)
    exit()
    filename = pf.Placeholder()
    read1 = Read(filename)
    tex = ToTexture(read1)
    rec709 = ToRec709(tex)
    
    # cache works if call Request print only once!
    result = evaluate(read1)

    # Create GUI
    app = QApplication()
    window = VideoPlayer()

    def update():
        #
        frame = window.frame()
        # run graph
        filename = "C:/Users/and/Desktop/SMPTE_colorbars/SMPTE_colorbars_#####.jpg"
        m = re.search("#+", filename) # match hashtags
        filename = filename[0:m.span()[0]]+f"%0{m.span()[1]-m.span()[0]}d"+filename[m.span()[1]:] # convert to printf style
        read1 = Read(filename)

        window.setImage(im)
        


    window.frameChanged.connect(update)

    window.show()
    sys.exit(app.exec_())

    filename = Constant("https://www.andraszalavari.com/assets/media/200130_MG_1696.jpg")


    print(np.array(result))



