from PySide2.QtWidgets import QWidget, QOpenGLWidget, QApplication, QVBoxLayout, QHBoxLayout, QFrame, QDial, QPushButton, QSpinBox, QSizePolicy
from PySide2.QtGui import QMouseEvent,QWheelEvent
from PySide2.QtCore import Qt



class LinearDial(QDial):
    def __init_(self, parent=None):
        super().__init_(parent=parent)
        self.lastValue = None
        self.lastPos = None

    def mousePressEvent(self, event):
        self.lastValue = self.value()
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        delta = event.pos()-self.lastPos
        self.setValue(self.lastValue+(delta.x()-delta.y())/10 )

    def mouseReleaseEvent(self, event):
        delta = event.pos()-self.lastPos
        self.setValue(self.lastValue+(delta.x()-delta.y())/10 )

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = LinearDial()
    def on_change(val):
        print("value changed", val)
    w.valueChanged.connect(on_change)
    w.show()
    sys.exit(app.exec_())