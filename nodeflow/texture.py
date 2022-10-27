

from dataclasses import dataclass
from OpenGL.GL import *

import numpy as np
from core import Operator, Constant


@dataclass(frozen=False)
class Texture:
    tex:int
    def __init__(self, tex:int=-1):
        self.tex = int(tex)
        if self.tex == -1:
            self.tex = int(glGenTextures( 1 ))
            print(self.tex)

    def __del__(self):
        if self.tex>0:
            print("delete texture:", self.tex, type(self.tex))
            glDeleteTextures([self.tex])


class ToTexture(Operator):
    def __init__(self, image: Operator):
        super().__init__(image)

    def __call__(self, img:np.ndarray):
        # GLFormat from numpy shape
        height, width, channels = img.shape
        if channels==1:
            glformat = GL_RED
        elif channels==2:
            glformat = GL_RG
        elif channels==3:
            glformat = GL_RGB
        elif channels==4:
            glformat=GL_RGBA
        else:
            raise NotImplementedError

        # GLType from numpy dtype
        if img.dtype == np.uint8:
            gltype = GL_UNSIGNED_BYTE
        elif img.dtype == np.float16:
            gltype = GL_HALF_FLOAT
        elif img.dtype == np.float32:
            gltype = GL_FLOAT
        else:
            raise NotImplementedError

        # Match internal format
        internalformat = None
        if internalformat is None: 
            if glformat is GL_RED:
                if gltype is GL_UNSIGNED_BYTE: internalformat=GL_R8
                elif gltype is GL_HALF_FLOAT: internalformat=GL_R16F
                elif gltype is GL_FLOAT: internalformat=GL_R32F
                else: raise NotImplementedError
            elif glformat is GL_RG:
                if gltype is GL_UNSIGNED_BYTE: internalformat=GL_RG8
                elif gltype is GL_HALF_FLOAT: internalformat=GL_RG16F
                elif gltype is GL_FLOAT: internalformat=GL_RG32F
                else: raise NotImplementedError
            elif glformat is GL_RGB:
                if gltype is GL_UNSIGNED_BYTE: internalformat=GL_RGB8
                elif gltype is GL_HALF_FLOAT: internalformat=GL_RGB16F
                elif gltype is GL_FLOAT: internalformat=GL_RGB32F
                else: raise NotImplementedError
            elif glformat is GL_RGBA:
                if gltype is GL_UNSIGNED_BYTE: internalformat=GL_RGBA8
                elif gltype is GL_HALF_FLOAT: internalformat=GL_RGBA16F
                elif gltype is GL_FLOAT: internalformat=GL_RGBA32F
                else: raise NotImplementedError
            else:
                raise NotImplementedError

        # Update texture
        tex = glGenTextures( 1 )
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER) # parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, internalformat, width, height, 0, glformat, gltype, img) # to GPU
        # glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

        return Texture(tex) # take ownership, delete if unused

        
class ToRec709(Operator):
    def __init__(self, texture:Operator):
        super().__init__(texture)

    def __call__(self, texture: Texture):
        colored_texture = "HELLO COLORSPACE"
        return colored_texture

if __name__ == "__main__":
    import sys
    from PySide2.QtWidgets import QApplication
    from gui.glviewer import GLViewer
    app = QApplication(sys.argv)
    viewer = GLViewer()
    viewer.show()
    
    #=========================
    from core import evaluate
    from image import Read, Ramp

    # Graph
    ramp = Ramp((512,512))
    filename = Constant("C:/users/and/desktop/nodeflow/tests/SMPTE_colorbars/SMPTE_colorbars_00001.jpg")
    read = Read(filename)
    to_tex = ToTexture(read)
    out = to_tex

    # display
    result = evaluate(out)
    viewer.setTexture(result.tex)
    sys.exit(app.exec_())