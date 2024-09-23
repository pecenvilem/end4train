from io import BytesIO
from typing import Callable

from PySide6.QtWidgets import QMainWindow, QAbstractItemView

from end4train.traces_model import TracesModel
from end4train.main_window_ui import Ui_MainWindow
from end4train.dataframe_model import PandasModel


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self,
                 toggle_listener_callback: Callable,
                 request_download_callback: Callable,
                 select_traces_callback: Callable,
                 trace_item_model: TracesModel,
                 data_table_model: PandasModel,
                 map_object
                 ):
        super().__init__()
        self.setupUi(self)
        self.hot_btn.setChecked(True)

        self.toggle_listener_callback = toggle_listener_callback
        self.request_download_callback = request_download_callback
        self.select_traces_callback = select_traces_callback
        self.traces_list_view.setModel(trace_item_model)
        self.traces_list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table_view.setModel(data_table_model)

        self.show_map(map_object)

        self.chart_view.setBackground("white")

        self.record_box.stateChanged.connect(self.toggle_listener)
        self.load_btn.clicked.connect(self.request_download)
        self.traces_list_view.clicked.connect(self.request_trace_change)

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

    def show_map(self, map_object) -> None:
        data = BytesIO()
        map_object.save(data, close_file=False)
        self.web_engine_view.setHtml(data.getvalue().decode())
