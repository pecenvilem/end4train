from pathlib import Path
from typing import List, Callable

import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QDialog
from pandas.core.dtypes.common import is_numeric_dtype

from end4train.app.settings import Settings
from end4train.config.app import COMPANY, APP_NAME, SettingsKey
from end4train.ui.dataframe_model import PandasModel
from end4train.ui.main_window import MainWindow
from end4train.ui.settings_dialog import SettingsDialog
from end4train.ui.traces_model import TracesModel


class Gui(QApplication):
    def __init__(
            self, argv: list[str],
            shutdown_callback: Callable,
            starting_data: pd.DataFrame,
            toggle_listener: Callable[[str, bool], None],
            download_log: Callable[[str], None],
            load_file: Callable[[Path], None],
            app_settings: Settings,
            save_settings_callback: Callable[[Settings], None]
    ) -> None:
        super().__init__(argv)

        self.app_settings = app_settings
        self.qt_settings = QSettings(
            QSettings.Format.IniFormat, QSettings.Scope.UserScope, COMPANY, APP_NAME
        )

        self.aboutToQuit.connect(shutdown_callback)

        self.load_file_callback = load_file
        self.save_settings_callback = save_settings_callback

        self.data = starting_data
        self.data_model = PandasModel(self.data)

        self.traces_model = TracesModel()
        self.plot_traces = {}

        self.main_window = MainWindow(
            toggle_listener, download_log, self.select_traces, self.traces_model, self.data_model, self.qt_settings,
            self.app_settings, self.edit_settings
        )
        self.main_window.actionOpen_log.triggered.connect(self.load_file)

        self.plot = self.main_window.plot
        self.main_window.open_btn.clicked.connect(self.load_file)

        self.styleHints().setColorScheme(self.app_settings.theme.color_scheme)
        self.setStyle(self.app_settings.theme.style)

        self.main_window.show()

    def load_file(self) -> None:
        file, selected_filter = QFileDialog.getOpenFileName(parent=self.main_window)
        if not file:
            return
        self.load_file_callback(Path(file))

    def edit_settings(self):
        dialog = SettingsDialog(self.main_window, self.app_settings)
        dialog.show()
        dialog.exec()
        if dialog.result() != QDialog.DialogCode.Accepted:
            return
        self.app_settings = dialog.get_settings()
        self.save_settings_callback(self.app_settings)
        self.styleHints().setColorScheme(self.app_settings.theme.color_scheme)
        self.setStyle(self.app_settings.theme.style)

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
