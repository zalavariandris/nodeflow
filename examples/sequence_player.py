from nodeflow.gui.timeline import Timeline
from nodeflow.gui.glviewer import GLViewer

from PySide2.QtWidgets import QWidget, QSizePolicy
from PySide2.QtCore import QSize

import pythonflow as pf

class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("sequence player")

        self.viewer = GLViewer()
        self.timeline = Timeline()


        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.viewer)
        self.viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout().addWidget(self.timeline)

        self.timeline.valueChanged.connect(self.evaluate)

    def evaluate(self, frame):
        print("evaluate", frame)

    def size(self):
        return QSize(720, 576)
        
        
if __name__ == "__main__":
    # PySide
    from PySide2.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QFrame, QDial, QPushButton, QSpinBox, QSizePolicy, QAbstractSpinBox, QStackedLayout
    from PySide2.QtGui import QMouseEvent,QWheelEvent, QPainter
    from PySide2.QtCore import Qt, Signal, QTimer

    app = QApplication()
    window = Window()
    window.resize(720, 576)
    window.show()
    app.exec_()
