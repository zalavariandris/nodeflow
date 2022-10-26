import sys

from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtWidgets import QSlider, QLabel, QVBoxLayout
from PIL import Image
import numpy as np
from typing import Union

class VideoPlayer(QWidget):
    frameChanged = Signal()
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("VideoPlayer")

        # Viewer
        self.viewer = QLabel()
        self.viewer.setScaledContents(True)
        self.viewer.setMinimumSize(500,500)
        self.viewer.setMaximumSize(500,500)

        # Frameslider
        self.frameslider = QSlider(orientation=Qt.Horizontal)
        self.frameslider.setMinimum(1)
        self.frameslider.setMaximum(100)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.viewer)
        self.layout().addWidget(self.frameslider)

        self.frameslider.valueChanged.connect(self.frameChanged)

    def frame(self):
        return self.frameslider.value()

    def setImage(self, img: Union[np.ndarray, Image.Image]):
        if isinstance(img, Image.Image):
            data = img.tobytes("raw","RGB")
            qim = QImage(data, img.size[0], img.size[1], QImage.Format_RGB888)
            self.viewer.setPixmap(QPixmap.fromImage(qim))
        elif isinstance(img, np.ndarray):
            img = (img*255).astype(np.uint8)
            height, width, channels = img.shape
            print(img.shape)
            bytesPerLine = channels * width
            qim = QImage(img.data, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGB888)
            self.viewer.setPixmap(QPixmap.fromImage(qim))
        else:
            raise NotImplementedError


if __name__ == "__main__":
    

    app = QApplication(sys.argv)

    window = VideoPlayer()
    def update():
        print(window.frame())
    window.frameChanged.connect(update)
    window.show()

    sys.exit(app.exec_())
