from typing import Sequence

from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import QDialog, QWidget

from end4train.ui.settings_dialog_ui import Ui_SettingsDialog

class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent: QWidget, styles: Sequence[str]):
        super().__init__(parent)
        self.setupUi(self)
        styles_model = QStringListModel(styles)
        self.style_combobox.setModel(styles_model)