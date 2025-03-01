from typing import Callable

from PySide6.QtCore import QUrl, QSettings, QEvent
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QAbstractItemView

from end4train.app.traces_model import TracesModel
from end4train.config.app import COMPANY, APP_NAME, WINDOW_STATE_KEY, WINDOW_GEOMETRY_KEY, \
     SaveOwner, SETTINGS_VERSION_NUMBER
from end4train.config.dummy_device import TEST_HOT_HOST, TEST_EOT_HOST
from end4train.ui.main_window_ui import Ui_MainWindow
from end4train.app.dataframe_model import PandasModel


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self,
                 toggle_listener_callback: Callable,
                 request_download_callback: Callable,
                 select_traces_callback: Callable,
                 trace_item_model: TracesModel,
                 data_table_model: PandasModel,
                 ):
        super().__init__()
        self.setupUi(self)
        self.settings = QSettings(
            QSettings.Format.IniFormat, QSettings.Scope.UserScope, COMPANY, APP_NAME
        )
        self.load_settings()

        self.actionSave_Layout.triggered.connect(lambda: self.save_settings(SaveOwner.USER))
        self.actionReset_Layout.triggered.connect(lambda: self.load_settings(SaveOwner.USER))

        self.hot_btn.setChecked(True)

        self.toggle_listener_callback = toggle_listener_callback
        self.request_download_callback = request_download_callback
        self.select_traces_callback = select_traces_callback
        self.traces_list_view.setModel(trace_item_model)
        self.traces_list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setModel(data_table_model)

        self.plot.setBackground("white")
        # TODO: replace PyQtGraph with pglive https://github.com/domarm-comat/pglive/tree/main

        self.record_box.stateChanged.connect(self.toggle_listener)
        self.load_btn.clicked.connect(self.request_download)
        self.traces_list_view.clicked.connect(self.request_trace_change)

        self.map.setSource(QUrl.fromLocalFile("ui/map.qml"))
        if self.map.errors():
            print(self.map.errors())
        self.map.show()

        # TODO: remove (just code to try a few things out...)
        # self.map.rootObject().property("position")
        # timer = QTimer(self)
        # timer.timeout.connect(lambda: self.map.rootObject().setProperty("position", QGeoCoordinate(50.1, 14.5)))
        # timer.start(5000)

    def load_settings(self, owner: SaveOwner = SaveOwner.SHUTDOWN_AUTOSAVE) -> None:
        # TODO: fix - settings object
        state = self.settings.value(f"{WINDOW_STATE_KEY}/{owner}")
        geometry = self.settings.value(f"{WINDOW_GEOMETRY_KEY}/{owner}")
        self.restoreState(state, SETTINGS_VERSION_NUMBER)
        self.restoreGeometry(geometry)

    def save_settings(self, owner: SaveOwner = SaveOwner.SHUTDOWN_AUTOSAVE) -> None:
        self.settings.setValue(f"{WINDOW_STATE_KEY}/{owner}", self.saveState(SETTINGS_VERSION_NUMBER))
        self.settings.setValue(f"{WINDOW_GEOMETRY_KEY}/{owner}", self.saveGeometry())

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
        return list(item.data() for item in self.traces_list_view.selectionModel().selectedRows())

    def closeEvent(self, event: QCloseEvent) -> bool:
        self.save_settings()
        return False
