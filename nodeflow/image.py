from typing import Callable, Any, Hashable
from core import Operator, Constant, evaluate
from pathlib import Path

import PIL
from PIL import Image
from PIL.ImageEnhance import Contrast
import numpy as np


# === DATA ===
from dataclasses import dataclass

@dataclass(frozen=True)
class Texture:
    def __init__(self, tex:int=-1):
        if self.tex == -1:
            self.tex = glGenTextures( 1 )

    def __del__(self):
        if self.tex>0:
            glDeleteTextures([self.tex])

# === IMAGE OPERATORS ===
from urllib.request import urlopen
import imageio
class Read(Operator):
    def __init__(self, url:Constant):
        super().__init__(url)

    def __call__(self, url:Path):
        return Image.open(urlopen(url))

# === OPENGL OPERATORS ===
from OpenGL.GL import *
class ToTexture(Operator):
    def __init__(self, image: Operator):
        super().__init__(image)

    def __call__(self, img:np.ndarray):
        if self.tex is not None:
            glDeleteTextures([self.tex])

        from gui.glhelpers import make_texture
        self.tex = make_texture(img)
        return Texture(self.tex)


class ToRec709(Operator):
    def __init__(self, texture:Operator):
        super().__init__(texture)

    def __call__(self, texture: Texture):
        colored_texture = "HELLO COLORSPACE"
        return colored_texture

# === MAIN ===
if __name__ == "__main__":
    import sys
    from gui.videoplayer import VideoPlayer
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
        filename = pf.placeholder('filename')
        image = (imageio.imread(filename).set_name('imread')[..., :3] / 255.0)
        cached = pf.cache(image, load_cache, save_cache, key=filename)
        cached.set_name("out")


    #print(result)
    #filename = Placeholder()
    #read1 = Read(filename)
    #tex = ToTexture(read1)
    #rec709 = ToRec709(tex)
    
    # cache works if call Request print only once!
    #result = evaluate(read1)

    # Create GUI
    app = QApplication()
    window = VideoPlayer()

    def hashtags_to_printf(filename):
        import re
        """convert hashtags to printf"""
        hashtag_match = re.search("#+", filename) # match hashtags
        if hashtag_match is not None: # convert hastag to printf style
            span = hashtag_match.span()
            filename = filename[0:span[0]]+f"%0{span[1]-span[0]}d"+filename[span[1]:] # convert to printf style
            return filename
        else:
            raise NotImplementedError

    def update():
        #
        frame = window.frame()
        # run graph
        filename = "C:/Users/and/Desktop/SMPTE_colorbars/SMPTE_colorbars_#####.jpg"
        filename = hashtags_to_printf(filename)
        filename = filename % frame
        #read1 = Read(filename)

        result = graph('out', filename=filename)
        window.setImage(result)
        
    window.frameChanged.connect(update)

    window.show()
    sys.exit(app.exec_())

    filename = Constant("https://www.andraszalavari.com/assets/media/200130_MG_1696.jpg")


    print(np.array(result))



