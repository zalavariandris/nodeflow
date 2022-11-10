import nodeflow as nf
import numpy as np

@nf.operator
def GetSequenceItem(path, F):
    return str(path).format(frame=F)

class ReadClip(nf.Operator):
    def __init__(self, clipname:nf.Operator, name=None):
        self.frame = nf.Variable(0)
        super().__init__(clipname, self.frame)
        filename = GetSequenceItem(clipname, self.frame)
        self.out = nf.image.Read(filename, self.frame)

    def __call__(self, clipname, F):
        pass
        # self.clipname.value = clipname
        # return self.clip


class Blur(nf.Operator):
    def __call__(self, clip):
        return nf.image.GaussianBlur(self.out)


class Echo(nf.Operator):
    def __call__(self, clip:nf.Operator):
        clip1 = nf.Operator.copy(clip)
        clip1.frame.value = nf.Plus(clip.frame, nf.Constant(1))
        return nf.image.Blend(clip, clip1)


class GetImage(nf.Operator):
    def __call__(self, clip:nf.Operator, F:int)->np.ndarray:
        clip.frame.value = F
        return clip.image_graph.evaluate()


if __name__ == "__main__":
    F = 50
    read = ReadClip(nf.Variable("./hello"))
    # echo = Echo(read)
    # image = GetImage(echo, nf.Variable(F))

    # Display Graph
    from nodeflow.gui.simplegraph import SimpleGraph


    from PySide2.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    viewer = SimpleGraph()
    viewer.setWindowTitle("Simple Graph viewer")
    viewer.show()
    # G = image.graph()
    # viewer.setGraph(G)
    sys.exit(app.exec_())