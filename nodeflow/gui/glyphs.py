import sys

from PySide2.QtWidgets import QApplication, QGridLayout, QPushButton, QStyle, QWidget


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        codes = [unicode for unicode in range(0x2300, 0x23FF)]
        layout = QGridLayout()
        for n, code in enumerate(codes):
            glyph = chr(code)
            btn = QPushButton(glyph + " " + format(code, 'X'))
            layout.addWidget(btn, n / 16, n % 16)
        # icons = sorted([attr for attr in dir(QStyle) if attr.startswith("SP_")])
        # layout = QGridLayout()

        # for n, name in enumerate(icons):
        #     btn = QPushButton(name)
        #     layout.addWidget(btn, n / 4, n % 4)

        self.setLayout(layout)


app = QApplication(sys.argv)

w = Window()
w.show()

app.exec_()