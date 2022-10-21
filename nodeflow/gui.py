import os
import PySide2
import sys

from PySide2 import QtCore, QtWidgets, QtGui
import matplotlib
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    frame = QtWidgets.QMainWindow()
    frame.setGeometry(50, 50, 600, 400)
    frame.setWindowTitle('FrameTitle')

    frame.show()

    sys.exit(app.exec_())