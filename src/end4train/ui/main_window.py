from typing import Callable

from PySide6.QtCore import QUrl, QSettings, QEvent
from PySide6.QtGui import QCloseEvent, Qt
from PySide6.QtWidgets import QMainWindow, QAbstractItemView

from end4train.ui.traces_model import TracesModel
from end4train.config.app import COMPANY, APP_NAME, SETTINGS_VERSION_NUMBER, SaveOwner, SettingsKey
from end4train.config.dummy_device import TEST_HOT_HOST, TEST_EOT_HOST
from end4train.ui.main_window_ui import Ui_MainWindow
from end4train.ui.dataframe_model import PandasModel
from end4train.app.settings import Settings


class MainWindow(QMainWindow, Ui_MainWindow):

    # TODO: add treeview for browsing data sources
    # TODO: add widget for displaying variable visualisations

    def __init__(self,
                 toggle_listener_callback: Callable,
                 request_download_callback: Callable,
                 select_traces_callback: Callable,
                 trace_item_model: TracesModel,
                 data_table_model: PandasModel,
                 qt_settings: QSettings,
                 app_settings: Settings,
                 edit_theme: Callable
                 ):
        super().__init__()
        self.setupUi(self)
        self.qt_settings = qt_settings
        self.load_layout()

        self.actionSave_Layout.triggered.connect(lambda: self.save_layout(SaveOwner.USER))
        self.actionReset_Layout.triggered.connect(lambda: self.load_layout(SaveOwner.USER))
        self.actionSettings.triggered.connect(edit_theme)

        self.hot_btn.setChecked(True)

        self.toggle_listener_callback = toggle_listener_callback
        self.request_download_callback = request_download_callback
        self.select_traces_callback = select_traces_callback
        self.traces_tree_view.setModel(trace_item_model)
        self.traces_tree_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.plot.setBackground("white")
        # TODO: replace PyQtGraph with pglive https://github.com/domarm-comat/pglive/tree/main

        self.record_box.stateChanged.connect(self.toggle_listener)
        self.load_btn.clicked.connect(self.request_download)
        self.traces_tree_view.clicked.connect(self.request_trace_change)

        self.map.setSource(QUrl.fromLocalFile("ui/map.qml"))
        if self.map.errors():
            print(self.map.errors())
        self.map.show()

        # TODO: remove (just code to try a few things out...)
        # self.map.rootObject().property("position")
        # timer = QTimer(self)
        # timer.timeout.connect(lambda: self.map.rootObject().setProperty("position", QGeoCoordinate(50.1, 14.5)))
        # timer.start(5000)

    def load_layout(self, owner: SaveOwner = SaveOwner.SHUTDOWN_AUTOSAVE) -> None:
        state = self.qt_settings.value(f"{SettingsKey.WINDOW_STATE}/{owner}")
        geometry = self.qt_settings.value(f"{SettingsKey.GEOMETRY_STATE}/{owner}")
        self.restoreState(state, SETTINGS_VERSION_NUMBER)
        self.restoreGeometry(geometry)

    def save_layout(self, owner: SaveOwner = SaveOwner.SHUTDOWN_AUTOSAVE) -> None:
        self.qt_settings.setValue(f"{SettingsKey.WINDOW_STATE}/{owner}", self.saveState(SETTINGS_VERSION_NUMBER))
        self.qt_settings.setValue(f"{SettingsKey.GEOMETRY_STATE}/{owner}", self.saveGeometry())

    def toggle_listener(self):
        self.toggle_listener_callback(
            self.get_selected_host(),
            self.record_box.isChecked()
        )

    def get_selected_host(self) -> str:
        if self.hot_btn.isChecked():
            return TEST_HOT_HOST
        return TEST_EOT_HOST

    def request_download(self):
        self.request_download_callback(self.get_selected_host())

    def request_trace_change(self):
        self.select_traces_callback(self.get_selected_traces())

    def get_selected_traces(self):
        return list(item.data() for item in self.traces_tree_view.selectionModel().selectedRows())

    def closeEvent(self, event: QCloseEvent) -> bool:
        self.save_layout()
        return False
