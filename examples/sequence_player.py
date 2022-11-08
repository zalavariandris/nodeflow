from nodeflow.gui.timeline import Timeline
from nodeflow.gui.glviewer import GLViewer

from PySide2.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout, QGridLayout
from PySide2.QtCore import QSize

import nodeflow as nf
from nodeflow.gui.simplegraph import SimpleGraph

from pathlib import Path


class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("sequence player")

        self.graphview = SimpleGraph()
        self.viewer = GLViewer()
        self.timeline = Timeline()
        self.timeline.setMinimum(1)
        self.timeline.setMaximum(100)
        self.timeline.setInpoint(1)
        self.timeline.setOutpoint(100)
        self.graph = SimpleGraph()

        # Connect Signals
        self.timeline.valueChanged.connect(self.evaluate)

        # Layout widgets
        self.setLayout(QGridLayout())
        self.layout().addWidget(self.graph,0,0,0,1)
        self.layout().addWidget(self.viewer, 0,1)
        self.layout().addWidget(self.timeline,1,1)

        self.layout().setVerticalSpacing(0)
        self.layout().setHorizontalSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)

        self.layout().setColumnStretch(0, 0.0)
        self.layout().setColumnStretch(1, 1.0)
        

        self.viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create processing graph
        frame=1
        self.filename = nf.Variable(str(Path.cwd() / Path(f"tests/SMPTE_colorbars/SMPTE_colorbars_{frame:05d}.jpg") ))

        read = nf.Log(nf.Read(self.filename), fmt="read")
        cached_read = nf.Cache(read)
        tex = nf.texture.ToTexture(cached_read)
        self.out = tex

        self.graph.setGraph(self.out.graph())

    def evaluate(self, frame):
        from pathlib import Path
        # get current filename by frame
        self.filename.value = str(Path.cwd() / Path(f"tests/SMPTE_colorbars/SMPTE_colorbars_{frame:05d}.jpg") )

        # evaluate graph
        result = self.out.evaluate()
        
        # keep texture object in memory
        self.tex = result

        # pass texture id to glviewer for display
        self.viewer.setTexture(result.tex)

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
