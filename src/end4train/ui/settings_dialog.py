import sys

from PySide6.QtWidgets import QDialog, QWidget, QApplication

from end4train.ui.model_view import SettingsModel, Delegate
from end4train.ui.settings_dialog_ui import Ui_SettingsDialog

class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setupUi(self)
        model = SettingsModel(parent)
        delegate = Delegate()
        self.treeView.setModel(model)
        self.treeView.setItemDelegate(delegate)
        self.treeView.expanded.connect(lambda index: self.treeView.resizeColumnToContents(index.column()))
        self.treeView.resizeColumnToContents(0)
        self.treeView.resizeColumnToContents(1)


def main(args: list[str]):
    app = QApplication(args)
    dialog = SettingsDialog(app.activeWindow())
    dialog.show()
    app.exec()

if __name__ == '__main__':
    main(sys.argv)
