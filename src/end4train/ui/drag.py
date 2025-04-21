import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel,
    QPushButton, QSizePolicy, QScrollArea, QVBoxLayout
)
from PySide6.QtCore import Qt, QMimeData, QPoint, QRect
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor, QDragEnterEvent, QDropEvent

class DraggableWidget(QWidget):
    """
    A base class for draggable widgets.  This class makes a widget
    draggable and provides a way to customize the appearance of the
    drag feedback.

    Attributes:
        drag_enabled (bool):  If True, the widget can be dragged.
    """
    def __init__(self, parent=None, drag_enabled=True):
        super().__init__(parent)
        self.drag_enabled = drag_enabled
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def mousePressEvent(self, event):
        """
        Called when the mouse is pressed.  If dragging is enabled,
        this method initiates a drag operation.
        """
        if self.drag_enabled and event.button() == Qt.MouseButton.LeftButton:
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
            painter = QPainter(pixmap)
            # Use a transparent background.
            painter.fillRect(QRect(0, 0, self.width(), self.height()), QColor(0, 0, 0, 0))
            self.render(painter.device())  # Draw the widget onto the pixmap
            painter.end()
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
        self.setStyleSheet("background-color: lightblue; border: 1px solid blue;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

class DropGrid(QWidget):
    """
    A widget that accepts dropped widgets and arranges them in a grid.
    """
    def __init__(self, parent=None, rows=3, cols=3):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setSpacing(5)  # Add some spacing between widgets
        self.grid_layout.setContentsMargins(0, 0, 0, 0) # Remove margins, if needed.

        self.rows = rows
        self.cols = cols
        self.cells = {}  # Store the widgets in a dictionary

        # Create empty cells in the grid.  These are just placeholders.
        for row in range(rows):
            for col in range(cols):
                # Use a QWidget as a placeholder.  A QLabel also works.
                placeholder = QWidget()
                placeholder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.grid_layout.addWidget(placeholder, row, col)
                self.cells[(row, col)] = None  # Initially, no widget in the cell

        self.setAcceptDrops(True)  # This is crucial for accepting drops!
        self.setStyleSheet("background-color: lightgray; border: 2px solid gray;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Called when a drag operation enters the widget.  We need to
        accept the event if we want to allow dropping.
        """
        if event.mimeData().hasText():
            event.acceptProposedAction()  # Accept the proposed action (e.g., move)
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """
        Called when a drag operation is completed (i.e., the mouse is released)
        over the widget.  This is where we handle the dropping of the widget.
        """
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

    def get_row_col_from_position(self, pos: QPoint):
        """
        Helper method to determine the row and column of a grid cell
        from a given position within the grid.
        """
        # Get the number of rows and columns in the grid.
        rows = self.grid_layout.rowCount()
        cols = self.grid_layout.columnCount()

        # Calculate the width and height of the grid.
        grid_rect = self.geometry()
        grid_width = grid_rect.width()
        grid_height = grid_rect.height()

        # Calculate the width and height of each cell.
        cell_width = grid_width / cols
        cell_height = grid_height / rows

        # Calculate the row and column based on the position.
        row = int(pos.y() / cell_height)
        col = int(pos.x() / cell_width)

        # Make sure the row and column are within the valid range.
        if 0 <= row < rows and 0 <= col < cols:
            return row, col
        else:
            return None, None

    def get_widget_position(self, widget):
        """
        Helper method to get the row and column of a widget in the grid.
        """
        for (row, col), stored_widget in self.cells.items():
            if stored_widget == widget:
                return row, col
        return None, None
        # for row in range(self.grid_layout.rowCount()):
        #     for col in range(self.grid_layout.columnCount()):
        #         if self.grid_layout.itemAtPosition(row, col) is not None:
        #             item_widget = self.grid_layout.itemAtPosition(row, col).widget()
        #             if item_widget == widget:
        #                 return row, col
        # return None, None

class ExampleApp(QScrollArea):
    """
    Main application window.  Uses a QScrollArea to contain the grid
    and draggable widgets.
    """
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)  # Make the content widget resizable
        self.viewport().setAutoFillBackground(False)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create a main widget to hold the layout.
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)  # Use a VBoxLayout
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.main_widget)

        # Create the drop grid.
        self.drop_grid = DropGrid(self.main_widget, rows=3, cols=3)
        self.main_layout.addWidget(self.drop_grid)  # Add grid to main layout

        # Create some draggable labels.
        label1 = DraggableLabel("Label 1", self.main_widget)
        label2 = DraggableLabel("Label 2", self.main_widget)
        label3 = DraggableLabel("Label 3", self.main_widget)
        label4 = DraggableLabel("Label 4", self.main_widget) # Add more labels
        label5 = DraggableLabel("Label 5", self.main_widget)

        # Add the labels to the main layout, not the grid layout.
        self.main_layout.addWidget(label1)
        self.main_layout.addWidget(label2)
        self.main_layout.addWidget(label3)
        self.main_layout.addWidget(label4)
        self.main_layout.addWidget(label5)

        # Create a button to add more widgets.
        add_button = QPushButton("Add Widget", self.main_widget)
        add_button.clicked.connect(self.add_widget_to_grid)
        self.main_layout.addWidget(add_button)

        self.setWindowTitle("Drag and Drop Grid Example")
        self.setGeometry(100, 100, 600, 400)

    def add_widget_to_grid(self):
        """
        Adds a new DraggableLabel to the grid.  It finds the first empty
        cell and adds the widget there.
        """
        # Find the first empty cell in the grid.
        for row in range(self.drop_grid.rows):
            for col in range(self.drop_grid.cols):
                if self.drop_grid.cells[(row, col)] is None:
                    new_label = DraggableLabel(f"New {row},{col}", self.main_widget)
                    self.drop_grid.grid_layout.addWidget(new_label, row, col)
                    self.drop_grid.cells[(row, col)] = new_label
                    return  # Exit after adding one widget

        # If no empty cell is found, you might want to display a message.
        print("No empty cells available!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    example_app = ExampleApp()
    example_app.show()
    sys.exit(app.exec())
