from functools import partial
from pathlib import Path
from typing import List, Callable

import pandas as pd
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QFileDialog, QStyleFactory
from PySide6.QtCore import Qt, QSettings
from pandas.core.dtypes.common import is_numeric_dtype

from end4train.app.device_connectors import OnLineListener, LogDownloader, DataSource
from end4train.app.settings import Settings
from end4train.ui.traces_model import TracesModel
from end4train.config.app import COMPANY, APP_NAME, SettingsKey
from end4train.config.paths import RECORD_OBJECT_KSY_PATH, SETTINGS_JSON_FILE
from end4train.communication.decode import decode_log_file, merge_type_specific_dataframes, decode_p_packet, \
    pivot_per_variable, parse_p_packet
from end4train.communication.ksy import KSYInfoStore
from end4train.ui.main_window import MainWindow
from end4train.ui.dataframe_model import PandasModel
from end4train.ui.settings_dialog import SettingsDialog


# TODO: rework using AnyIO
# TODO: design a way to call teardown for TimsDevice.stop()
# TODO: add device discovery (see. scratch.txt and handwritten notes)

# TODO: add map

# TODO: remove table

# TODO: use pglive

# TODO: add analog gauges (possibly implement a simple one from scratch...)

# TODO: add UI for selecting style and possibly overriding color theme


class Gui(QApplication):
    def __init__(
            self, argv: List[str],
            shutdown_callback: Callable,
            starting_data: pd.DataFrame,
            toggle_listener: Callable[[str, bool], None],
            download_log: Callable[[str], None],
            load_file: Callable[[Path], None],
            app_settings: Settings
    ) -> None:
        super().__init__(argv)

        self.app_settings = app_settings
        self.qt_settings = QSettings(
            QSettings.Format.IniFormat, QSettings.Scope.UserScope, COMPANY, APP_NAME
        )

        self.aboutToQuit.connect(shutdown_callback)

        self.load_file_callback = load_file

        self.data = starting_data
        self.data_model = PandasModel(self.data)

        self.traces_model = TracesModel()
        self.plot_traces = {}

        self.main_window = MainWindow(
            toggle_listener, download_log, self.select_traces, self.traces_model, self.data_model, self.qt_settings,
            self.app_settings, self.edit_theme
        )
        self.main_window.actionOpen_log.triggered.connect(self.load_file)

        self.plot = self.main_window.plot
        self.main_window.open_btn.clicked.connect(self.load_file)

        self.main_window.show()

    def load_file(self) -> None:
        file, selected_filter = QFileDialog.getOpenFileName(parent=self.main_window)
        if not file:
            return
        self.load_file_callback(Path(file))


    def set_theme(self):
        self.set_style()
        self.set_color_scheme()

    def set_color_scheme(self):
        color_scheme = self.app_settings.value(f"{SettingsKey.COLOR_SCHEME}")
        if not isinstance(color_scheme, int):
            self.styleHints().setColorScheme(Qt.ColorScheme.Unknown)
            return
        self.styleHints().setColorScheme(Qt.ColorScheme(color_scheme))


    def set_style(self):
        style = self.settings.value(f"{SettingsKey.WINDOW_STATE}")
        if style is None:
            return
        self.setStyle("windows11")

    def edit_theme(self):
        # styles = [style.lower() for style in QStyleFactory.keys()]

        dialog = SettingsDialog(self.main_window, self.app_settings)
        dialog.accepted.connect(self.store_theme)
        dialog.setModal(True)
        dialog.open()

    def store_theme(self):
        pass

    def select_traces(self, selection):
        self.data_model.set_new_data(self.data[selection])
        for trace in self.plot_traces.copy():
            if trace not in selection:
                self.delete_plot(trace)
        for trace in selection:
            if trace not in self.plot_traces:
                self.add_plot(trace)

    def add_plot(self, trace: str):
        if not is_numeric_dtype(self.data[trace]):
            return
        self.plot.nextRow()
        plot = self.plot.addPlot(axisItems={'bottom': pg.DateAxisItem()})
        try:
            reference_plot = next(iter(self.plot_traces.values()))["plot_area"]
        except StopIteration:
            pass
        else:
            plot.setXLink(reference_plot)
        plot.setLabel("left", text=trace)
        data = self.data[trace].dropna()
        line = plot.plot(data.index.astype('int64') // 10 ** 9, data.to_list())
        self.plot_traces[trace] = {
            "plot_area": plot,
            "data_line": line
        }

    def delete_plot(self, trace: str):
        plot_info = self.plot_traces.pop(trace)
        self.plot.removeItem(plot_info["plot_area"])

    def update_plot(self, traces: List[str]):
        for trace in traces:
            data = self.data[trace].dropna()
            self.plot_traces[trace]["data_line"].setData(data.index.astype('int64') // 10 ** 9, data.to_list())


    def add_data(self, data: pd.DataFrame) -> None:
        self.data = pd.concat([self.data, data])
        # TODO: if possible, don't sort repeatedly
        self.data = self.data.sort_index()
        selected_traces = self.main_window.get_selected_traces()
        self.data_model.set_new_data(self.data[selected_traces])
        self.traces_model.update_traces(self.data.columns.tolist())
        self.update_plot(list(self.plot_traces.keys()))


class Monitor:
    def __init__(self, argv: List[str]):
        self.data = pd.DataFrame()

        self.settings = Settings.model_validate_json(SETTINGS_JSON_FILE.read_text(), by_name=True)
        self.gui_app = Gui(
            argv, self.shutdown, self.data, self.toggle_listener, self.download_log, self.load_file, self.settings
        )

        self.ksy_info_store = KSYInfoStore(RECORD_OBJECT_KSY_PATH)
        self.listener = OnLineListener(partial(self.add_data, source=DataSource.P_PACKET))
        self.downloader = LogDownloader(self.add_data, "hot")

    def shutdown(self):
        self.listener.stop("hot")
        self.listener.stop("eot")
        self.downloader.stop()

    def download_log(self, host: str):
        self.downloader = LogDownloader(self.add_data, host)
        self.downloader.download()

    def add_data(self, data, source: DataSource):
        if source == DataSource.LOG_FILE:
            loaded_data = decode_log_file(data, self.ksy_info_store.get_class_to_kaitai_type_map())
        elif source == DataSource.P_PACKET:
            loaded_data = parse_p_packet(data, self.ksy_info_store.get_class_to_kaitai_type_map())
        else:
            return
        # dataframe = merge_type_specific_dataframes(list(loaded_data.values()))
        # dataframe = pivot_per_variable(dataframe)
        dataframes = [pivot_per_variable(dataframe) for dataframe in loaded_data.values()]
        dataframe = pd.concat(dataframes, axis="columns")
        self.data = pd.concat([self.data, dataframe])
        # TODO: if possible, don't sort repeatedly
        self.data = self.data.sort_index()
        self.gui_app.add_data(dataframe)

    def toggle_listener(self, host: str, listen: bool):
        if listen:
            self.listener.listen(host)
        else:
            self.listener.stop(host)

    def load_file(self, file: Path):
        with open(file, "rb") as f:
            data = f.read()
        self.add_data(data, DataSource.LOG_FILE)

    def run(self):
        self.gui_app.exec()