from typing import Tuple
from webbrowser import Opera
from pathlib import Path

import numpy as np
import cv2

from nodeflow.core import Operator, Constant


class Read(Operator):
    def __init__(self, filename:Operator, name=None):
        super().__init__(filename, name=name)

    def __call__(self, filename:str):
        if not Path(filename).exists():
            raise FileNotFoundError(filename)
        print("read file")
        return cv2.imread(filename).astype(np.float32)/255.0

    def key(self):
        return ("Read", self.args[0].key())


class Ramp(Operator):
    def __init__(self, size: Tuple[int, int], name:str=None):
        super().__init__(name=name)
        self.width, self.height = size

    def __call__(self):
        R, G = np.mgrid[0:1.0:720j, 0:1.0:1280j].astype(np.float32)
        B = np.zeros(shape=R.shape, dtype=np.float32)
        rgb = np.dstack([R, G, B])
        return rgb

    def key(self):
        return ("Ramp", self.width, self.height)


import cv2
class GaussianBlur(Operator):
    def __init__(self, img:Operator, name=None):
        super().__init__(img, name=name)

    def __call__(self, img:np.ndarray):
        return cv2.GaussianBlur(img,(75,75),0)


class BilateralFilter(Operator):
    def __init__(self, img:Operator, name=None):
        super().__init__(img, name=name)

    def __call__(self, img:np.ndarray):
        return cv2.bilateralFilter(img,90,75,75)


class Resize(Operator):
    def __init__(self, img:Operator, size:Operator):
        super().__init__(img, size)

    def __call__(self, img:np.ndarray, size:Tuple[int, int]):
        return cv2.resize(img, size)


class Blend(Operator):
    def __init__(self, A:Operator, B:Operator, mix:Operator):
        super().__init__(A, B, mix)

    def __call__(self, A:np.ndarray, B:np.ndarray, mix:float):
        assert(A.shape == B.shape)
        return A*(1-mix) + B*mix


if __name__ == "__main__":

    filename = Constant("C:/users/and/desktop/nodeflow/tests/SMPTE_colorbars/SMPTE_colorbars_00001.jpg")
    read = Read(filename)
    blur = GaussianBlur(read)
    bilateral = BilateralFilter(read)
    ramp = Ramp((512,512))
    thumb_read = Resize(read, Constant((128,128)))
    thumb_ramp = Resize(ramp, Constant((128,128)))
    thumbs_blend = Blend(thumb_read, thumb_ramp, Constant(0.5))

    import matplotlib.pyplot as plt
    import math
    ops = [read, blur, bilateral, ramp, thumb_read, thumbs_blend]
    fig = plt.figure()
    cols = math.ceil(math.sqrt(len(ops)))
    rows = math.ceil(len(ops)/cols)
    for i, op in enumerate(ops):
        ax = fig.add_subplot(rows,cols,i+1)
        ax.set_title(f"{op}")
        ax.imshow(op.evaluate())

    plt.show()

