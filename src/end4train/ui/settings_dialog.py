from typing import Iterable

from PySide6.QtWidgets import QDialog

from end4train.ui.settings_dialog_ui import Ui_SettingsDialog


class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, styles: Iterable[str]):
        super().__init__()
        self.setupUi(self)



        self.style_combobox.insertItems()