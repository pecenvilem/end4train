import sys
from pathlib import Path

from PySide6.QtWidgets import QDialog, QWidget, QApplication, QHeaderView, QDialogButtonBox

from end4train.ui.model_view import Settings, SettingsModel, Delegate
from end4train.ui.settings_dialog_ui import Ui_SettingsDialog

SETTINGS_JSON_FILE = Path("settings.json")

class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent: QWidget, settings: Settings):
        super().__init__(parent)
        self.setupUi(self)
        self.model = SettingsModel(parent, settings)
        delegate = Delegate()
        self.tree_view.setModel(self.model)
        self.tree_view.setItemDelegate(delegate)
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tree_view.expandAll()
        self.button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.reset)

    def reset(self) -> None:
        self.model.reset()
        self.tree_view.expandAll()

    def get_settings(self) -> Settings:
        return self.model.settings


def main(args: list[str]):
    app = QApplication(args)

    settings = Settings.model_validate_json(SETTINGS_JSON_FILE.read_text(), by_name=True)

    dialog = SettingsDialog(app.activeWindow(), settings)
    dialog.show()
    app.exec()
    if dialog.result() == QDialog.DialogCode.Accepted:
        SETTINGS_JSON_FILE.write_text(settings.model_dump_json(indent=4))

if __name__ == '__main__':
    main(sys.argv)
