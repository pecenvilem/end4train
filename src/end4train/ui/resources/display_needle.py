from PySide6.QtCore import QTimer, QPoint
from PySide6.QtGui import QTransform, QVector3D
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import QGraphicsView, QApplication, QGraphicsScene, QGraphicsRotation

from end4train.config.paths import NEEDLE_SVG_FILE
from end4train.config.ui import NEEDLE_CENTRE

if __name__ == '__main__':
    app = QApplication()
    view = QGraphicsView()
    scene = QGraphicsScene()
    view.setInteractive(True)
    item = QGraphicsSvgItem(str(NEEDLE_SVG_FILE))
    item.setElementId("needle")
    rotation = QGraphicsRotation(origin=QVector3D(NEEDLE_CENTRE), angle=0)
    item.setTransformations([rotation])
    item.setFlag(QGraphicsSvgItem.GraphicsItemFlag.ItemIsMovable)
    timer = QTimer(app, interval=10)
    timer.timeout.connect(lambda: rotation.setAngle(rotation.angle() + .5))
    timer.start()
    scene.addItem(item)
    view.setScene(scene)
    view.setInteractive(False)
    view.scale(5, 5,)
    view.show()
    app.exec()
