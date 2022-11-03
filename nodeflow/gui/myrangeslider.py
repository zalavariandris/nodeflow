from PySide2.QtWidgets import QWidget, QApplication, QPushButton
from PySide2.QtGui import QMouseEvent,QWheelEvent
from PySide2.QtCore import Qt, QSize, Signal, QEvent, QPoint, QObject

class Thumb(QPushButton):
    # def mouseMoveEvent(self, event):
    #     super().mouseMoveEvent(event)
    #     event.ignore()

    def sizeHint(self):
        return QSize(8, 22)

    # def mousePressEvent(self, event):
    #     event.ignore()

    # def paintEvent(self, event):
    #     pass

class MyRangeSlider(QWidget):
    lowerValueChanged = Signal(int)
    upperValueChanged = Signal(int)
    def __init__(self, parent:QWidget=None):
        super().__init__(parent=parent)
        self._lowerValue = 0
        self._upperValue = 100
        self._minimum = 0
        self._maximum = 100

        # subwidgets
        self.span = Thumb(self)
        # self.span.setFlat(True)

        self.left_thumb = Thumb(self)
        # self.left_thumb.setFlat(True)
        self.left_thumb.setCursor(Qt.SizeHorCursor)

        self.right_thumb = Thumb(self)
        # self.right_thumb.setFlat(True)
        self.right_thumb.setCursor(Qt.SizeHorCursor)

        self.span.installEventFilter(self)
        self.left_thumb.installEventFilter(self)
        self.right_thumb.installEventFilter(self)

    def _to_pos(self, val):
        val = int(val)
        val-=self.minimum()
        val/=self.maximum()-self.minimum()+1
        val*=self.width()
        return val

    def _to_value(self, x):
        x/=self.width()
        x*=self.maximum()-self.minimum()+1
        x+=self.minimum()
        return int(x)

    def showEvent(self, event):
        self._updateElements()
        self.update()

    def resizeEvent(self, event):
        self._updateElements()
        self.update()

    def lowerValue(self):
        return self._lowerValue

    def setLowerValue(self, val:int):
        if val == self._lowerValue:
            return

        self._lowerValue = val

        if self.upperValue()<=val:
            self.setUpperValue(val+1)

        self.lowerValueChanged.emit(val)
        self._updateElements()
        self.update()

    def upperValue(self):
        return self._upperValue

    def setUpperValue(self, val):
        if val == self._upperValue:
            return

        self._upperValue = val

        if self.lowerValue()>=val:
            self.setLowerValue(val-1)

        self.upperValueChanged.emit(val)
        self._updateElements()
        self.update()
    
    def minimum(self):
        return self._minimum

    def setMinimum(self, val):
        if val == self._minimum:
            return
 
        self._minimum = val
        if self.maximum() <= val:
            self.setMaximum(val+1)

        self._updateElements()
        self.update()

    def maximum(self):
        return self._maximum

    def setMaximum(self, val):
        if val == self._maximum:
            return

        self._maximum = val
        if self.minimum() >= val:
            self.setMinimum(val-1)
        self._updateElements()
        self.update()

    def reset(self):
        self.setLowerValue(self.minimum())
        self.setUpperValue(self.maximum())

    def mouseDoubleClickEvent(self, event):
        self.reset()


    def eventFilter(self, obj:QObject, event:QEvent):
        if event.type() == QEvent.MouseButtonDblClick:
            self.reset()
            return True

        delta = QPoint()
        if event.type() == QEvent.MouseButtonPress:
            self._lastpos = event.screenPos()
            self._lastvalues = self.lowerValue(), self.upperValue()
            return True

        if event.type() == QEvent.MouseMove:
            delta_value = self._to_value(event.screenPos().x()) - self._to_value(self._lastpos.x())

            if obj is self.span:
                self.setLowerValue(self._lastvalues[0]+delta_value)
                self.setUpperValue(self._lastvalues[1]+delta_value)

            if obj is self.left_thumb:
                self.setLowerValue(self._lastvalues[0]+delta_value)

            if obj is self.right_thumb:
                self.setUpperValue(self._lastvalues[1]+delta_value)

            return True


        if event.type() == QEvent.MouseButtonRelease:
            return True

        return False


    def mouseReleaseEvent(self, event):
        pass

    def _updateElements(self):
        # x1 = self._to_pos(self.lowerValue())
        # x11 = self._to_pos(self.lowerValue()+1)
        # tick_width = x11-x1

        left = self._to_pos(self.lowerValue())
        right = self._to_pos(self.upperValue()+1)

        self.left_thumb.setFixedHeight(self.height())
        # self.left_thumb.setFixedWidth(tick_width)
        self.left_thumb.move(left-self.left_thumb.width()/2, 0)
        self.right_thumb.setFixedHeight(self.height())
        # self.right_thumb.setFixedWidth(tick_width)
        self.right_thumb.move(right-self.right_thumb.width()/2, 0)

        if right-left<=0:
            if self.span.isVisible():
                self.span.hide()
        else:
            if not self.span.isVisible():
                self.span.show()

            self.span.setFixedHeight(self.height())
            self.span.move(left, 0)
            self.span.setFixedWidth(right-left)


if __name__ == "__main__":
    app = QApplication().instance() or QApplication()
    w = MyRangeSlider()
    w.resize(500, 100)
    w.setMinimum(20)
    w.setMaximum(80)
    
    
    w.setLowerValue(40)
    w.setUpperValue(60)

    print("min max", w.minimum(), w.maximum())
    print("low, up", w.lowerValue(), w.upperValue())

    def on_lower_change(val):
        print(f"[{w.minimum()}-{w.maximum()}]")
        print("lowerValueChanged", val)
    w.lowerValueChanged.connect(on_lower_change)

    def on_upper_change(val):
        print(f"[{w.minimum()}-{w.maximum()}]")
        print("upperValueChanged", val)
    w.upperValueChanged.connect(on_upper_change)

    w.show()
    app.exec_()