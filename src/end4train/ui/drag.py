import sys
from numbers import Number
from random import choice

from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel,
    QPushButton, QSizePolicy, QScrollArea, QVBoxLayout, QStyle, QMainWindow, QMenuBar
)
from PySide6.QtCore import Qt, QMimeData, QPoint, QRect, QSize, QPointF
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor, QDragEnterEvent, QDropEvent, QIcon, QAction


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


class DropGrid(QWidget):
    """
    A widget that accepts dropped widgets and arranges them in a grid.
    """
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        self._edit_mode = True
        menu = QMenuBar(self)
        action = QAction(self)
        action.setIcon(QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties)))
        action.triggered.connect(self.toggle_edit_mode)
        menu.addAction(action)
        self.grid_layout.setMenuBar(menu)
        self._placeholders: list[QWidget] = []
        for row in range(3):
            for column in range(3):
                self.place_placeholder(row, column)
        center_widget = QLabel(self)
        center_widget.setText("Drop widgets here...")
        self.place_widget(center_widget, 1, 1)
        self.exit_edit_mode()

        self.setAcceptDrops(True)

    def place_widget(self, widget: QWidget, row: int, column: int) -> None:
        # get LayoutItem currently at [row, column] and delete it from layout and Qt pointers
        current_item = self.grid_layout.itemAtPosition(row, column)
        try:
            self._placeholders.remove(current_item.widget())
        except ValueError:
            pass
        current_item.widget().hide()
        current_item.widget().deleteLater()
        self.grid_layout.removeItem(current_item)


        # insert new widget at [row, column] in layout
        self.grid_layout.addWidget(widget, row, column, Qt.AlignmentFlag.AlignCenter)
        if row == 0:
            self.shift_rows()
        if column == 0:
            self.shift_columns()
        if row == self.grid_layout.rowCount() - 1:
            self.add_row()
        if column == self.grid_layout.columnCount() - 1:
            self.add_column()

    def place_placeholder(self, row: int, column: int) -> None:
        placeholder = self.get_placeholder()
        self.grid_layout.addWidget(placeholder, row, column, Qt.AlignmentFlag.AlignCenter)
        self._placeholders.append(placeholder)

    def shift_rows(self) -> None:
        last_row = self.grid_layout.rowCount() - 1
        last_column = self.grid_layout.columnCount() - 1
        for row in range(last_row, -1, -1):
            for column in range(last_column, -1, -1):
                widget = self.grid_layout.itemAtPosition(row, column).widget()
                self.grid_layout.removeWidget(widget)
                self.grid_layout.addWidget(widget, row + 1, column, Qt.AlignmentFlag.AlignCenter)
        for column in range(self.grid_layout.columnCount()):
            self.place_placeholder(0, column)

    def shift_columns(self) -> None:
        last_row = self.grid_layout.rowCount() - 1
        last_column = self.grid_layout.columnCount() - 1
        for row in range(last_row, -1, -1):
            for column in range(last_column, -1, -1):
                widget = self.grid_layout.itemAtPosition(row, column).widget()
                self.grid_layout.removeWidget(widget)
                self.grid_layout.addWidget(widget, row, column + 1, Qt.AlignmentFlag.AlignCenter)
        for row in range(self.grid_layout.rowCount()):
            self.place_placeholder(row, 0)

    def add_row(self) -> None:
        next_row = self.grid_layout.rowCount()
        for column in range(self.grid_layout.columnCount()):
            self.place_placeholder(next_row, column)

    def add_column(self) -> None:
        next_column = self.grid_layout.columnCount()
        for row in range(self.grid_layout.rowCount()):
            self.place_placeholder(row, next_column)

    def get_row_col_from_position(self, pos: QPointF) -> tuple[int, int]:
        """
        Helper method to determine the row and column of a grid cell
        from a given position within the grid.
        """
        # Get the number of rows and columns in the grid.
        rows = self.grid_layout.rowCount()
        cols = self.grid_layout.columnCount()

        # Calculate the width and height of the grid.
        grid_width = self.geometry().width()
        grid_height = self.geometry().height()

        # Calculate the width and height of each cell.
        cell_width = grid_width / cols
        cell_height = grid_height / rows

        # Calculate the row and column based on the position.
        row = int(pos.y() / cell_height)
        col = int(pos.x() / cell_width)

        # Make sure the row and column are within the valid range.
        if not (0 <= row < rows and 0 <= col < cols):
            raise ValueError(f"Row: {row}, column: {col} out of bounds of {rows}, {cols}")
        return row, col

    def get_placeholder(self) -> QWidget:
        placeholder = QPushButton(self)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        placeholder.setIcon(icon)
        return placeholder

    def toggle_edit_mode(self) -> None:
        if self._edit_mode:
            self.exit_edit_mode()
        else:
            self.enter_edit_mode()


    def enter_edit_mode(self) -> None:
        self._edit_mode = True
        for placeholder in self._placeholders:
            placeholder.show()

    def exit_edit_mode(self) -> None:
        self._edit_mode = False
        for placeholder in self._placeholders:
            placeholder.hide()

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
        try:
            row, column = self.get_row_col_from_position(event.position())
        except ValueError:
            self.exit_edit_mode()
            event.ignore()
            return

        widget = DraggableWidget(self)
        label = QLabel(widget)
        label.setText(event.mimeData().text())
        widget.setLayout(QVBoxLayout(widget))
        widget.layout().addWidget(label)
        self.place_widget(widget, row, column)
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
