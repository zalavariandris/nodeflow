# PySide
from PySide2.QtWidgets import QWidget, QComboBox, QSlider, QOpenGLWidget, QApplication, QVBoxLayout, QHBoxLayout, QFrame, QDial, QPushButton, QSpinBox, QSizePolicy, QAbstractSpinBox, QStackedLayout
from PySide2.QtGui import QMouseEvent,QWheelEvent, QPainter
from PySide2.QtCore import Qt, Signal, QTimer

from enum import Enum

from nodeflow.gui.lineardial import LinearDial
from nodeflow.gui.myrangeslider import MyRangeSlider
from nodeflow.gui.frameslider import Frameslider
from nodeflow.gui.cachebar import CacheBar


class Direction(Enum):
    FORWARD = 1
    BACKWARD = 2

class LoopMode(Enum):
    REPEAT = 0
    BOUNCE = 1
    STOP = 2
    CONTINUE = 3

class Timeline(QWidget):
    valueChanged = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Timeline")
        self._value = 0
        self._minimum = 0
        self._maximum = 100
        self._fps = 24
        self._inpoint = 0
        self._outpoint = 100
        self._play_direction = Direction.FORWARD

        self.setStyleSheet("""
        QSpinBox{
            background-color: rgba(128,128,128,0.0);
            border: none;
            border-radius: 5px;
        }
        QSpinBox:hover{
            background-color: rgba(128,128,128,0.2);
        }
        QSpinBox:focus{
            background-color: rgba(128,128,128,0.2);
        }
        QPushButton {

        }
        QFrame{
            border: none;
        }

        QComboBox{
            background-color: transparent;
        }
        QComboBox:hover{
            background-color: rgba(128,128,128,0.2);
        }
        QComboBox::drop-down {
            border-width: 0px;
            width: 0px;
        }
        QComboBox::drop-down {
            border-width: 0px;
            width: 0px;
        }
        QComboBox::down-arrow {
            background-color: transparent;
        }

        """)

        # Create Time Controls (frame slider and playback controls)
        # --------------------------------------------------------
        
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        # self.layout().setSpacing(0)

        # Create Slider Controls
        # ======================


        # Framedial
        self.frame_dial = LinearDial()
        self.frame_dial.setMinimum(self._minimum)
        self.frame_dial.setMaximum(self._maximum)
        # frame_dial.setWrapping(True) # seem to crash when?
        self.frame_dial.setFixedSize(26,26)
        self.frame_dial.valueChanged.connect(self.setValue)

        # first frame spinner
        self.first_frame_spinner = QSpinBox()
        self.first_frame_spinner.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.first_frame_spinner.setAlignment(Qt.AlignRight)
        self.first_frame_spinner.setValue(self.minimum())
        self.first_frame_spinner.setMinimum(-999999)
        self.first_frame_spinner.setMaximum(+999999)
        self.first_frame_spinner.setToolTip("first frame")
        self.first_frame_spinner.valueChanged.connect(self.setMinimum)

        # last frame spinner
        self.last_frame_spinner = QSpinBox()
        self.last_frame_spinner.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.last_frame_spinner.setValue(self.maximum())
        self.last_frame_spinner.setMinimum(-999999)
        self.last_frame_spinner.setMaximum(+999999)
        self.last_frame_spinner.setToolTip("last frame")
        self.last_frame_spinner.valueChanged.connect(self.setMaximum)


        # frameslider
        self.frameslider = QSlider(orientation=Qt.Horizontal)
        self.frameslider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.frameslider.setTracking(True)
        self.frameslider.valueChanged.connect(self.setValue)

        # playback range slider
        self.playback_range_slider = MyRangeSlider()
        self.playback_range_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.playback_range_slider.setFixedHeight(8)
        self.playback_range_slider.setMinimum(self.minimum())
        self.playback_range_slider.setMaximum(self.maximum())
        self.playback_range_slider.setLowerValue(self.minimum())
        self.playback_range_slider.setUpperValue(self.maximum())
        self.playback_range_slider.lowerValueChanged.connect(self.setInpoint)
        self.playback_range_slider.upperValueChanged.connect(self.setOutpoint)

        # cache bar
        cacheBar = CacheBar()
        
        # Create playback controls
        # ========================

        # playback timer
        self._loopmode = LoopMode.REPEAT
        self.timer = QTimer()
        
        def step():
            val = self.value()
            if self._play_direction == Direction.FORWARD:
                val+=1
                if val>self.outpoint():
                    if self._loopmode == LoopMode.REPEAT:
                        val = self.inpoint()
                    elif self._loopmode == LoopMode.BOUNCE:
                        self._play_direction = Direction.BACKWARD
                        val = self.outpoint()-1
                    elif self._loopmode == LoopMode.STOP:
                        val = self.outpoint()
                        self.pause()
                    elif self._loopmode == LoopMode.CONTINUE:
                        pass
                    else:
                        raise ValueError

            elif self._play_direction == Direction.BACKWARD:
                val-=1
                if val<self.inpoint():
                    if self._loopmode == LoopMode.REPEAT: val = self.outpoint()
                    elif self._loopmode == LoopMode.BOUNCE:
                        self._play_direction = Direction.FORWARD
                        val = self.inpoint()+1
                    elif self._loopmode == LoopMode.STOP:
                        val = self.inpoint()
                        self.pause()
                    elif self._loopmode == LoopMode.CONTINUE:
                        pass
                    else:
                        raise ValueError
            else:
                raise ValueError

            self.setValue(val)

        self.timer.timeout.connect(step)

        # fps spinner
        self.fps_spinner = QSpinBox()
        self.fps_spinner.setToolTip("fps")
        self.fps_spinner.setSuffix("fps")
        self.fps_spinner.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.fps_spinner.setValue(self.fps())
        self.fps_spinner.valueChanged.connect(self.setFps)

        # loopmode dropdown
        self.loopmode_btn = QComboBox()
        self.loopmode_btn.addItems(["Repeat", "Bounce", "Stop", "Continue"])
        self.loopmode_btn.currentIndexChanged.connect(lambda idx: self.setLoopMode(LoopMode(idx)))

        self.play_forward_btn = QPushButton("\u23F5")
        self.play_forward_btn.setFixedWidth(26)
        self.play_forward_btn.pressed.connect(lambda: self.play(Direction.FORWARD))
        
        self.pause_forward_btn = QPushButton("||")
        self.pause_forward_btn.setFixedWidth(26)
        self.pause_forward_btn.pressed.connect(self.pause)

        self.play_backward_btn = QPushButton("\u23F4")
        self.play_backward_btn.setFixedWidth(26)
        self.play_backward_btn.pressed.connect(lambda: self.play(Direction.BACKWARD))

        self.pause_backward_btn = QPushButton("||")
        self.pause_backward_btn.setFixedWidth(26)
        self.pause_backward_btn.pressed.connect(self.pause)

        step_back_btn = QPushButton("|<")
        step_back_btn.setFixedWidth(26)
        step_back_btn.pressed.connect(self.step_backward)

        step_forward_btn = QPushButton(">|")
        step_forward_btn.setFixedWidth(26)
        step_forward_btn.pressed.connect(self.step_forward)

        skip_to_start_btn = QPushButton("|<<")
        skip_to_start_btn.setFixedWidth(26)
        skip_to_start_btn.pressed.connect(self.go_to_start)

        skip_to_end_btn = QPushButton(">>|")
        skip_to_end_btn.setFixedWidth(26)
        skip_to_end_btn.pressed.connect(self.go_to_end)
        
        self.frame_spinner = QSpinBox()
        self.frame_spinner.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.frame_spinner.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.frame_spinner.setAlignment(Qt.AlignHCenter)
        self.frame_spinner.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.frame_spinner.setToolTip("current frame")
        self.frame_spinner.valueChanged.connect(self.setValue)

        # Layout widgets
        # slider controls
        slider_controls = QFrame(self)
        slider_controls.setLayout(QHBoxLayout())
        slider_controls.layout().setContentsMargins(0,0,0,0)
        slider_controls.layout().setSpacing(0)
        slider_controls.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.layout().addWidget(slider_controls)
        slider_controls.layout().addWidget(self.frame_dial)
        slider_controls.layout().addWidget(self.first_frame_spinner)

        # slider middle frame
        middle = QFrame()
        middle.setLayout(QVBoxLayout())
        middle.layout().setContentsMargins(0,0,0,0)
        middle.layout().setSpacing(0)
        middle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        middle.layout().addWidget(self.playback_range_slider)  
        middle.layout().addWidget(self.frameslider)
        #middle.layout().addWidget(cacheBar)
        slider_controls.layout().addWidget(middle)
        slider_controls.layout().addWidget(self.last_frame_spinner)

        # playback controls
        self.forward_stack = QWidget()
        self.forward_stack.setFixedWidth(26)
        self.forward_stack.setLayout(QStackedLayout())
        self.forward_stack.layout().addWidget(self.play_forward_btn)
        self.forward_stack.layout().addWidget(self.pause_forward_btn)

        self.backward_stack = QWidget()
        self.backward_stack.setLayout(QStackedLayout())
        self.backward_stack.setFixedWidth(26)
        self.backward_stack.layout().addWidget(self.play_backward_btn)
        self.backward_stack.layout().addWidget(self.pause_backward_btn)

        playback_controls = QFrame()
        playback_controls.setLayout(QHBoxLayout())
        playback_controls.layout().setContentsMargins(0,0,0,0)
        playback_controls.layout().setSpacing(0)
        playback_controls.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.layout().addWidget(playback_controls)

        playback_controls.layout().addWidget(self.fps_spinner)
        playback_controls.layout().addWidget(self.loopmode_btn)
        playback_controls.layout().addWidget(skip_to_start_btn)
        playback_controls.layout().addWidget(step_back_btn)
        playback_controls.layout().addWidget(self.backward_stack)

        playback_controls.layout().addWidget(self.frame_spinner)
        playback_controls.layout().addWidget(self.forward_stack)
        playback_controls.layout().addWidget(step_forward_btn)
        playback_controls.layout().addWidget(skip_to_end_btn)

        for btn in [skip_to_start_btn, step_back_btn, self.play_backward_btn, self.play_forward_btn, self.pause_forward_btn, step_forward_btn, skip_to_end_btn]:
            btn.setFlat(True)

    def value(self):
        return self._value

    def setValue(self, val:int):
        if self._value == val:
            return
            
        self._value = val
        self.frame_dial.blockSignals(True)
        self.frame_dial.setValue(val)
        self.frame_dial.blockSignals(False)

        self.frameslider.blockSignals(True)
        self.frameslider.setValue(val)
        self.frameslider.blockSignals(False)

        self.frame_spinner.blockSignals(True)
        self.frame_spinner.setValue(val)
        self.frame_spinner.blockSignals(False)

        self.valueChanged.emit(val)

    def inpoint(self):
        return self._inpoint

    def setInpoint(self, val:int):
        self._inpoint = val

        self.playback_range_slider.blockSignals(True)
        self.playback_range_slider.setLowerValue(val)
        self.playback_range_slider.blockSignals(False)

        

    def outpoint(self):
        return self._outpoint

    def setOutpoint(self, val:int):
        self._outpoint = val
        self.playback_range_slider.blockSignals(True)
        self.playback_range_slider.setUpperValue(val)
        self.playback_range_slider.blockSignals(False)

    def loopMode(self):
        return self._loopmode

    def setLoopMode(self, val):
        print("set loop ode", val)
        self._loopmode = val

        self.loopmode_btn.blockSignals(True)
        self.loopmode_btn.setCurrentIndex(self._loopmode.value)
        self.loopmode_btn.blockSignals(False)

    def minimum(self):
        return self._minimum

    def setMinimum(self, val:int):
        self._minimum = val
        self.frameslider.setMinimum(val)
        self.playback_range_slider.setMinimum(val)

        self.first_frame_spinner.blockSignals(True)
        self.first_frame_spinner.setValue(val)
        self.first_frame_spinner.blockSignals(False)

    def maximum(self):
        return self._maximum

    def setMaximum(self, val:int):
        self._maximum = val
        self.frameslider.setMaximum(val)
        self.playback_range_slider.setMaximum(val)

        self.last_frame_spinner.blockSignals(True)
        self.last_frame_spinner.setValue(val)
        self.last_frame_spinner.blockSignals(False)

    def setFps(self, val:float):
        if self._fps == val:
            return

        self._fps = val
        self.fps_spinner.blockSignals(True)
        self.fps_spinner.setValue(val)
        self.fps_spinner.blockSignals(False)

        if self.timer.isActive():
            self.timer.setInterval(1000/self._fps if self._fps else 0)

    def fps(self):
        return self._fps

    def step_forward(self):
        self.setValue(self.value()+1)

    def step_backward(self):
        self.setValue(self.value()-1)

    def go_to_end(self):
        self.setValue(self.outpoint())

    def go_to_start(self):
        self.setValue(self.inpoint())

    def play(self, direction=Direction.FORWARD):
        if self._play_direction == direction and self.timer.isActive():
            # already playing in the same direction
            return
   
        if self.timer.isActive() and self._play_direction != direction:
            # already playing but switch direction
            self._play_direction = direction
            if self._play_direction == Direction.FORWARD:
                self.forward_stack.layout().setCurrentIndex(1)
                self.backward_stack.layout().setCurrentIndex(0)

            if self._play_direction == Direction.BACKWARD:
                self.forward_stack.layout().setCurrentIndex(0)
                self.backward_stack.layout().setCurrentIndex(1)
            return

        elif not self.timer.isActive():
            # start play
            self._play_direction = direction
            self.timer.start(1000/self.fps())
            if self._play_direction == Direction.FORWARD:
                self.forward_stack.layout().setCurrentIndex(1)

            if self._play_direction == Direction.BACKWARD:
                self.backward_stack.layout().setCurrentIndex(1)
            return

    def pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.forward_stack.layout().setCurrentIndex(0)
            self.backward_stack.layout().setCurrentIndex(0)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    timeline = Timeline()
    timeline.show()
    def on_change(frame):
        print("value changed", frame)
    timeline.valueChanged.connect(on_change)
    sys.exit(app.exec_())