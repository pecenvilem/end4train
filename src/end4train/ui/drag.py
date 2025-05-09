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
            # Get the ID of the dragged widget from the MIME data.
            widget_id = int(event.mimeData().text())

            # Find the dragged widget by its ID.  We have to iterate through
            # all child widgets to find it.  In a real application, you would
            # likely have a better way to manage your widgets (e.g., a dictionary).
            dragged_widget = None
            for child in self.parent().findChildren(QWidget): # changed to self.parent()
                if id(child) == widget_id:
                    dragged_widget = child
                    break

            if dragged_widget is None:
                event.ignore()
                return

            # Determine the row and column where the widget was dropped.
            pos = event.position().toPoint()
            row, col = self.get_row_col_from_position(pos)
            # print(f"Dropped at row: {row}, col: {col}") # Debugging

            if row is None or col is None:
                event.ignore()
                return

            # Check if the cell is already occupied.
            if self.cells[(row, col)] is not None:
                # Swap widgets.
                old_widget = self.cells[(row, col)]
                old_row, old_col = self.get_widget_position(old_widget)

                self.grid_layout.removeWidget(old_widget)
                self.grid_layout.removeWidget(dragged_widget)

                self.grid_layout.addWidget(dragged_widget, old_row, old_col)
                self.grid_layout.addWidget(old_widget, row, col)

                self.cells[(row, col)] = old_widget
                self.cells[(old_row, old_col)] = dragged_widget
            else:
                # Remove the widget from its old layout (if it has one)
                if dragged_widget.layout() is not None:
                    dragged_widget.layout().removeWidget(dragged_widget)
                # Add the widget to the grid layout.
                self.grid_layout.addWidget(dragged_widget, row, col)
                self.cells[(row, col)] = dragged_widget  # Store the widget in the cell
            event.accept()
        else:
            event.ignore()


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
