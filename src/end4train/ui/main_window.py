from typing import Callable

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QMainWindow, QAbstractItemView

from end4train.traces_model import TracesModel
from end4train.ui.main_window_ui import Ui_MainWindow
from end4train.dataframe_model import PandasModel


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
        self.hot_btn.setChecked(True)

        self.toggle_listener_callback = toggle_listener_callback
        self.request_download_callback = request_download_callback
        self.select_traces_callback = select_traces_callback
        self.traces_list_view.setModel(trace_item_model)
        self.traces_list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setModel(data_table_model)

        self.plot.setBackground("white")

        self.record_box.stateChanged.connect(self.toggle_listener)
        self.load_btn.clicked.connect(self.request_download)
        self.traces_list_view.clicked.connect(self.request_trace_change)

        self.map.setSource(QUrl.fromLocalFile("ui/map.qml"))
        print(self)
        self.map.show()

    def toggle_listener(self):
        self.toggle_listener_callback(
            self.get_selected_host(),
            self.record_box.isChecked()
        )

    def get_selected_host(self) -> str:
        if self.hot_btn.isChecked():
            return "hot"
        return "eot"

    def request_download(self):
        self.request_download_callback(self.get_selected_host())

    def request_trace_change(self):
        self.select_traces_callback(self.get_selected_traces())

    def get_selected_traces(self):
        return list(item.data() for item in self.traces_list_view.selectionModel().selectedRows())
