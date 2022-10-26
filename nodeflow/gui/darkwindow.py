from PySide2.QtWidgets import QPushButton, QWidget, QLabel, QFrame, QHBoxLayout, QVBoxLayout, QApplication, QSizePolicy
from PySide2.QtGui import QMouseEvent,QWheelEvent, QColor
from PySide2.QtCore import Qt, QSize

class DarkTitle(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        title = QLabel(self.parent().windowTitle() or "-no title-")
        close_btn = QPushButton("x")
        close_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        close_btn.clicked.connect(self.parent().close)

        self.setStyleSheet("""
            QLabel { color : white; background: transparent;}
            QPushButton {color: white; border: none; background: transparent;}
        """);

        self.setLayout(QHBoxLayout())

        close_btn.setFixedSize(32, 32)
        self.layout().addSpacing(32)
        self.layout().addStretch()
        self.layout().addWidget(title)
        self.layout().addStretch()
        self.layout().addWidget(close_btn)
        self.offset = None

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(27,33,35, 255))
        self.setPalette(p)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.cursor = event.globalPos() - self.parent().geometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent().move(event.globalPos() - self.offset)
            event.accept()

class DarkResizeGrip(QLabel):
    def __init__(self, parent=None):
        super().__init__("resize", parent=parent)
        self.setStyleSheet("background: red;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent().resize(self.size()+QSize(self.offset.x(), self.offset.y()))
            #self.parent().resize(self.size()+QSize(delta.x(), delta.y()))
            event.accept()
            self.offset = event.globalPos()



class DarkWindow(QWidget):
    def __init__(self, content:QWidget, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.resize(720, 512)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

        self.titlebar = DarkTitle(parent=self)
        self.titlebar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.content = content
        self.layout().addWidget(self.titlebar)
        self.layout().addWidget(self.content)
        self.resizegrip = DarkResizeGrip()
        self.layout().addWidget(self.resizegrip)




def main():
    import sys
    app = QApplication(sys.argv)
    window = DarkWindow(content=QWidget())
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()