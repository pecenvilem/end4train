import sys
from pathlib import Path

from PySide6.QtWidgets import QDialog, QWidget, QApplication, QHeaderView

from end4train.ui.model_view import Settings, SettingsModel, Delegate
from end4train.ui.settings_dialog_ui import Ui_SettingsDialog

SETTINGS_JSON_FILE = Path("settings.json")

class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent: QWidget, settings: Settings):
        super().__init__(parent)
        self.setupUi(self)
        model = SettingsModel(parent, settings)
        delegate = Delegate()
        self.tree_view.setModel(model)
        self.tree_view.setItemDelegate(delegate)
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

    # TODO: implement saving and default value restore


def main(args: list[str]):
    app = QApplication(args)

    settings = Settings.model_validate_json(SETTINGS_JSON_FILE.read_text(), strict=True)
    # TODO: DEBUG: some values are not loaded from the file - default are used eve if value is present in data
    #  breaking e.g.: ColorScheme, MinimumValue, tick-counts... pretty much all non-boolean and non-string items

    dialog = SettingsDialog(app.activeWindow(), settings)
    dialog.show()
    app.exec()
    if dialog.result() == QDialog.DialogCode.Accepted:
        SETTINGS_JSON_FILE.write_text(settings.model_dump_json(indent=4))

if __name__ == '__main__':
    main(sys.argv)
