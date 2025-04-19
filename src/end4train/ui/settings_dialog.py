import sys

from PySide6.QtWidgets import QDialog, QWidget, QApplication, QHeaderView

from end4train.ui.model_view import SettingsModel, Delegate
from end4train.ui.settings_dialog_ui import Ui_SettingsDialog

class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setupUi(self)
        model = SettingsModel(parent)
        delegate = Delegate()
        self.tree_view.setModel(model)
        self.tree_view.setItemDelegate(delegate)
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)


def main(args: list[str]):
    app = QApplication(args)
    dialog = SettingsDialog(app.activeWindow())
    dialog.show()
    app.exec()

if __name__ == '__main__':
    main(sys.argv)
