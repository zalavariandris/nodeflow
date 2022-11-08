from PySide2.QtWidgets import QWidget, QPlainTextEdit
from PySide2.QtGui import QTextCursor
import sys
class LogWindow(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setReadOnly(True)

    def write(self, txt):
        logwindow.moveCursor(QTextCursor.End)
        self.insertPlainText(txt)

    def __enter__(self):
        self._restore_stdout = sys.stdout
        sys.stdout = self

    def __exit__(self ,type, value, traceback):
        sys.stdout = self._restore_stdout

if __name__ == "__main__":
    import sys
    from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit
    app = QApplication()

    lineedit = QLineEdit()
    def on_enter():
        text = lineedit.text()
        
        with logwindow:
            print(text)
        lineedit.clear()
    
    lineedit.returnPressed.connect(on_enter)
    
    logwindow = LogWindow()

    # Layout widgets in a window
    window = QWidget()
    window.setWindowTitle("Log to widget example")
    window.setLayout(QVBoxLayout())
    window.layout().addWidget(logwindow)
    window.layout().addWidget(lineedit)
    lineedit.setFocus()
    
    # show gui
    window.show()
    app.exec_()