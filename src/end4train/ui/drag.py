import sys
from random import choice

from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel,
    QPushButton, QSizePolicy, QScrollArea, QVBoxLayout, QStyle, QMainWindow
)
from PySide6.QtCore import Qt, QMimeData, QPoint, QRect
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor, QDragEnterEvent, QDropEvent

class DraggableWidget(QWidget):
    """
    A base class for draggable widgets.  This class makes a widget
    draggable and provides a way to customize the appearance of the
    drag feedback.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        """
        Called when the mouse is pressed.  If dragging is enabled,
        this method initiates a drag operation.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Create a QDrag object for handling the drag-and-drop operation.
            drag = QDrag(self)
            # Create a QMimeData object to hold the data being dragged.  In this
            # case, we're just passing the object itself as a string.  For more
            # complex data, you might use a JSON string or a custom MIME type.
            mime_data = QMimeData()
            mime_data.setText(str(id(self)))  # Use id() for a unique identifier.  Avoid using the object itself.
            drag.setMimeData(mime_data)

            # Create a pixmap of the widget to be used as a visual
            # representation during the drag operation.
            pixmap = QPixmap(self.size())
            self.render(pixmap)  # Draw the widget onto the pixmap
            drag.setPixmap(pixmap)

            # Set the position of the cursor relative to the pixmap.  This
            # determines where the cursor will be relative to the dragged image.
            drag.setHotSpot(QPoint(int(event.position().x()), int(event.position().y())))

            # Start the drag-and-drop operation.  The type of operation
            # (copy, move, link) is determined by the target widget.
            drag.exec(Qt.DropAction.MoveAction)
        else:
            super().mousePressEvent(event)

class DraggableLabel(DraggableWidget):
    """
    A QLabel that can be dragged and dropped.
    """
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.label = QLabel(self)
        self.label.setText(text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

class DropGrid(QWidget):
    """
    A widget that accepts dropped widgets and arranges them in a grid.
    """
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        placeholder = QLabel()
        placeholder.setText("Drag widgets here...")
        self.grid_layout.addWidget(placeholder, 0, 0, Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)  # This is crucial for accepting drops!

    def dragEnterEvent(self, event: QDragEnterEvent):
        # TODO: Add widget insertion and placement
        if event.mimeData().hasText():
            event.acceptProposedAction()  # Accept the proposed action (e.g., move)
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        # TODO: Add widget insertion and placement
        if event.mimeData().hasText():
            # Determine the row and column where the widget was dropped.
            pos = event.position().toPoint()

            # Check if the cell is already occupied
                # Swap widgets.
                # Remove the widget from its old layout (if it has one)
                # Add the widget to the grid layout.


class SourceWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel(self)
        label.setText("Source widget...")
        layout.addWidget(label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            trace = choice(["Widget 1", "Widget 2", "Widget 3"])
            mime_data.setText(trace)
            drag.setMimeData(mime_data)
            label = QLabel()
            label.setText(trace)
            pixmap = QPixmap(self.size())
            pixmap.fill(self.palette().color(self.backgroundRole()))
            label.render(pixmap)
            drag.setPixmap(pixmap)
            drag.exec(Qt.DropAction.MoveAction)
        else:
            super().mousePressEvent(event)



class ExampleApp(QApplication):
    def __init__(self, argv: list[str]):
        super().__init__(argv)

        self.main_window = QMainWindow()
        self.main_window.setWindowTitle("Drag and Drop Grid Example")

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        source = SourceWidget()
        layout.addWidget(source)

        target = DropGrid()
        layout.addWidget(target)

        self.main_window.setCentralWidget(central_widget)
        self.main_window.show()


if __name__ == '__main__':
    app = ExampleApp(sys.argv)
    sys.exit(app.exec())
