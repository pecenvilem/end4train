import itertools
import re
from pathlib import Path
from typing import Generator, Any

from PySide6.QtCore import QTimer, QPointF, Qt, QRectF
from PySide6.QtGui import QVector3D, QMouseEvent
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import QGraphicsView, QApplication, QGraphicsScene, QGraphicsRotation

from lxml import etree

from end4train.config.paths import NEEDLE_SVG_FILE, OBE_RING_SVG_FILE, OBE_BASE_SVG_FILE
from end4train.config.ui import DEFAULT_NEEDLE_CENTRE, SVG_MAIN_GROUP_ITEM_ID, DEFAULT_OBE_BASE_CENTRE, \
    DEFAULT_OBE_RING_CENTRE, TRANSFORM_ATTRIBUTE_NAME, SVG_CENTRE_POINT_ITEM_ID, SVG_CENTRE_X, SVG_CENTRE_Y


def get_rotation_origin(svg_file: Path) -> QPointF | None:
    tree = etree.parse(str(svg_file))
    root = tree.getroot()
    namespaces = {'svg': 'http://www.w3.org/2000/svg'}
    main_element = root.find(f".//svg:*[@id='{SVG_CENTRE_POINT_ITEM_ID}']", namespaces=namespaces)
    if main_element is None:
        return None
    transform: str | None = main_element.get(TRANSFORM_ATTRIBUTE_NAME)
    if transform is None:
        return None
    transform = re.sub(r"\s", "", transform)
    match = re.match(r"translate\((?P<x>\d+(?:.\d+)?),(?P<y>\d+(?:.\d+)?)\)", transform)
    if not match:
        return None
    group_dict = match.groupdict()
    x, y = group_dict.get('x'), group_dict.get('y')
    if x is None or y is None:
        return None
    x, y = main_element.get(SVG_CENTRE_X), main_element.get(SVG_CENTRE_Y)
    if x is None or y is None:
        return None
    try:
        return QPointF(float(x), float(y))
    except ValueError:
        return None


def ring_position_generator() -> Generator[float, Any, Any]:
    indents = [-3, -1, 0, 1, 2, 3, 4, 3, 2, 1, 0, -1]
    yield from itertools.cycle([float(indent) * 15 for indent in indents])


class ZoomableView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setMouseTracking(True)
        self.drag_mode = False
        self.drag_start = QPointF()


    def wheelEvent(self, event):
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_mode = True
            self.drag_start = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drag_mode:
            delta = event.position() - self.drag_start
            self.drag_start = event.position()
            self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() - delta.x()))
            self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() - delta.y()))
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_mode = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            super().mouseReleaseEvent(event)

if __name__ == '__main__':
    app = QApplication()
    view = ZoomableView()
    scene = QGraphicsScene()

    base = QGraphicsSvgItem(str(OBE_BASE_SVG_FILE))
    centre_element_xform = base.renderer().transformForElement(SVG_CENTRE_POINT_ITEM_ID)
    origin = QPointF(centre_element_xform.dx(), centre_element_xform.dy())
    base.setTransformOriginPoint(origin)
    base.setPos(-origin)

    ring = QGraphicsSvgItem(str(OBE_RING_SVG_FILE))
    centre_element_xform = ring.renderer().transformForElement(SVG_CENTRE_POINT_ITEM_ID)
    origin = QPointF(centre_element_xform.dx(), centre_element_xform.dy())
    ring.setTransformOriginPoint(origin)
    ring.setPos(-origin)
    ring.setRotation(60)

    scene.addItem(base)
    scene.addItem(ring)
    view.setScene(scene)
    view.show()

    ring_timer = QTimer(app, interval=1000)
    generator = ring_position_generator()
    ring_timer.timeout.connect(lambda: ring.setRotation(next(generator)))
    ring_timer.start()

    app.exec()
