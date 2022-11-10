# PySide
from PySide2.QtWidgets import QWidget, QOpenGLWidget, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from PySide2.QtGui import QMouseEvent,QWheelEvent, QColor, QBrush, QPen, QPainter, QPainterPath, QPolygonF
from PySide2.QtCore import Qt, QRect, QLineF, QPointF
from typing import Dict, List
import math, random


class NodeItem(QGraphicsEllipseItem):
    def __init__(self, parent=None):
        size = 15
        super().__init__(QRect(-size/2,-size/2, size,size), parent=parent)

        self.outlets = [] # outgoing edges
        self.inlets = [] # incoming edges

        c = QColor(70,70,70)
        c.setAlpha(255)
        self.setBrush(c)

        self.setPen(QPen(QColor(20,20,20), 1.0))
        self.setPen(Qt.NoPen)

        self._label = QGraphicsTextItem(parent=self)
        self._label.setTextWidth(120)

        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)

    def setText(self, text):
        self._label.setPlainText(text)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.inlets:
                line = edge.line()
                edge.setLine(QLineF(line.p1(), self.pos()))
                edge.update()

            for edge in self.outlets:
                line = edge.line()
                edge.setLine(QLineF(self.pos(), line.p2()))
                edge.update()

        return super().itemChange(change, value)

class EdgeItem(QGraphicsLineItem ):
    def __init__(self, source, target, parent=None):
        super().__init__(parent=parent)

        source.outlets.append(self)
        target.inlets.append(self)

        self.setPen(QPen(QColor(20,20,20), 1.0))
        self.setLine(QLineF(source.pos(), target.pos()))

    def boundingRect(self):
        return super().boundingRect().adjusted(-30,-30,30,30)

    def paint(self, painter, option, widget):
        #super().paint(painter, option, widget)
        width, length = 10, 10
        arrowPoly = QPolygonF([QPointF(0,0), QPointF(-width/2,-length), QPointF(width/2,-length)])

        length = self.line().length()
        offset = 10
        arrow_line = QLineF(self.line().pointAt(offset/length), self.line().pointAt(1.0-offset/length))

        painter.setPen(QPen(QColor(30,30,30, 200), 1.0))
        painter.drawLine(arrow_line)
        
        painter.translate(arrow_line.p2())
        painter.rotate(-arrow_line.angle()-90)
        painter.setBrush(QColor(30,30,30, 200))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(arrowPoly)
        

def layered_layout(G, root):
    layer_indices = {root: 0} # Node: Layer idx

    def dfs(n):
        for s in G[n]:
            layer_indices[s] = layer_indices[n]+1

    dfs(root)

    layers:Dict[List] = dict()
    for n, idx in layer_indices.items():
        if idx not in layers:
            layers[idx] = []

        layers[idx].append(n)

    pos = dict() # N, (x,y)
    for y, nodes in layers.items():
        for x, n in enumerate(nodes):
            pos[n] = (x*100, y*100)

    return pos

from grandalf.graphs import Vertex,Edge,Graph,graph_core
def grandalf_layout(G, root=None):
    V = {n:Vertex(n) for n in G.keys()}
    E = []
    for n, sources in G.items():
        for s in sources:
            E.append(Edge(V[n], V[s]))

    g = Graph(V.values(), E)
    from grandalf.layouts import SugiyamaLayout
    class default_view:
        w, h=50.0,50.0
    for v in V.values(): v.view = default_view()
    sug = SugiyamaLayout(g.C[0])
    sug.init_all()
    sug.draw()

    pos = dict()
    for n, v in V.items():
        pos[n] = v.view.xy[0], -v.view.xy[1]
    return pos
    


class SimpleGraph(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing)

        self.setScene(QGraphicsScene())

    def setGraph(self, G):
        self.scene().clear()
        pos = grandalf_layout(G)
        self.nodes = dict()
        for n, (x, y) in pos.items():
            nodeitem = NodeItem()
            nodeitem.setToolTip(repr(n))
            nodeitem.setText(str(n))
            nodeitem.setPos(x, y)
            self.scene().addItem(nodeitem)
            self.nodes[n]=nodeitem

        self.edges = dict()
        for n, sources in G.items():
            for s in sources:
                edgeitem = EdgeItem(self.nodes[s], self.nodes[n])
                edgeitem.setZValue(-1)
                self.scene().addItem(edgeitem)
                self.edges[(n, s)]= edgeitem

    def node(self, key):
        return self.nodes[key]



if __name__ == "__main__":
    # create a graph
    from PySide2.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    viewer = SimpleGraph()
    viewer.setWindowTitle("Simple Graph viewer")
    viewer.show()
    G = {
        "A": ["B", "C"], 
        "B": [],
        "C": []
    }
    viewer.setGraph(G)
    sys.exit(app.exec_())
