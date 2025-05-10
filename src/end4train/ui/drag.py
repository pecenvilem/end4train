import sys
from numbers import Number
from random import choice

from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel,
    QPushButton, QSizePolicy, QScrollArea, QVBoxLayout, QStyle, QMainWindow
)
from PySide6.QtCore import Qt, QMimeData, QPoint, QRect, QSize, QPointF
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor, QDragEnterEvent, QDropEvent, QIcon


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
        self.widgets: list[QWidget] = []
        for i in range(3):
            for j in range(3):
                if i == 1 and j == 1:
                    center_widget = QLabel(self)
                    center_widget.setText("Drop widgets here...")
                    self.widgets.append(center_widget)
                    self.grid_layout.addWidget(center_widget, 1, 1)
                    continue
                self.grid_layout.addWidget(self.get_placeholder(), i, j, Qt.AlignmentFlag.AlignCenter)
        self.exit_edit_mode()
        self.setAcceptDrops(True)

    def get_placeholder(self) -> QLabel:
        placeholder = QLabel(self)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        placeholder.setPixmap(icon.pixmap(QSize(30, 30)))
        return placeholder

    def enter_edit_mode(self) -> None:
        for i in range(self.grid_layout.count()):
            self.grid_layout.itemAt(i).widget().show()

    def exit_edit_mode(self) -> None:
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if widget in self.widgets:
                continue
            widget.hide()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            self.enter_edit_mode()
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event, /):
        self.exit_edit_mode()

    def dropEvent(self, event: QDropEvent):
        if not event.mimeData().hasText():
            self.exit_edit_mode()
            event.ignore()
            return
        for i in range(self.grid_layout.count()):
            column, row, column_span, row_span = self.grid_layout.getItemPosition(i)
            if self.grid_layout.cellRect(row, column).contains(event.position().toPoint()):
                break
        else:
            self.exit_edit_mode()
            event.ignore()
            return
        # TODO: Add insertion of new row / column
        self.grid_layout.itemAtPosition(row, column).widget().deleteLater()
        self.grid_layout.removeItem(self.grid_layout.itemAtPosition(row, column))
        label = QLabel(self)
        label.setText(event.mimeData().text())
        self.widgets.append(label)
        self.grid_layout.addWidget(label, row, column)
        self.exit_edit_mode()
        event.accept()


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
            text = choice(["Widget 1", "Widget 2", "Widget 3"])
            mime_data.setText(text)
            drag.setMimeData(mime_data)
            label = QLabel()
            label.setText(text)
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
